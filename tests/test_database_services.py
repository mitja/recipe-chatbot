import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from typing import List # Maintained for clarity, though not strictly used in the final code

# Adjust path to import from the root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database_config import Base # Using get_db for session management in tests too
from database.models import Family, FamilyMember, ShoppingList, GenderEnum
from database import services # Import the services module

class TestDatabaseServices(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        # Provide a way to get a db session for service functions
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    # --- FamilyService Tests ---
    def test_create_family(self):
        family = services.create_family(self.db, name="The Service Family", slug="service-family")
        self.assertIsNotNone(family)
        self.assertEqual(family.name, "The Service Family")
        queried_family = self.db.query(Family).filter(Family.id == family.id).first() # Direct query to verify
        self.assertEqual(queried_family.slug, "service-family")

    def test_create_family_duplicate(self):
        services.create_family(self.db, name="Duplicate Family", slug="duplicate-slug")
        family2 = services.create_family(self.db, name="Duplicate Family", slug="another-slug")
        self.assertIsNone(family2, "Should return None for duplicate name")
        family3 = services.create_family(self.db, name="Another Family", slug="duplicate-slug")
        self.assertIsNone(family3, "Should return None for duplicate slug")

    def test_get_family_by_slug(self):
        services.create_family(self.db, name="Slug Family", slug="find-me-slug")
        family = services.get_family_by_slug(self.db, "find-me-slug")
        self.assertIsNotNone(family)
        self.assertEqual(family.name, "Slug Family")
        family_none = services.get_family_by_slug(self.db, "nonexistent-slug")
        self.assertIsNone(family_none)

    def test_get_family_by_id(self):
        created_family = services.create_family(self.db, name="ID Family", slug="id-family")
        self.assertIsNotNone(created_family) # Ensure creation was successful
        family = services.get_family_by_id(self.db, created_family.id)
        self.assertIsNotNone(family)
        self.assertEqual(family.name, "ID Family")
        family_none = services.get_family_by_id(self.db, 999) # Non-existent ID
        self.assertIsNone(family_none)

    # --- FamilyMemberService Tests ---
    def test_add_family_member(self):
        family = services.create_family(self.db, name="Member Test Family", slug="member-test-family")
        self.assertIsNotNone(family, "Family creation failed in setUp for test_add_family_member")
        member = services.add_family_member(
            self.db, family_id=family.id, name="Jane Service", gender=GenderEnum.FEMALE, age_years=28
        )
        self.assertIsNotNone(member)
        self.assertEqual(member.name, "Jane Service")
        self.assertEqual(member.family_id, family.id)
        self.assertEqual(member.gender, GenderEnum.FEMALE)

    def test_add_family_member_family_not_found(self):
        member = services.add_family_member(self.db, family_id=999, name="Ghost Member") # Non-existent family_id
        self.assertIsNone(member)

    def test_get_family_members_summary_csv(self):
        family = services.create_family(self.db, name="Summary CSV Family", slug="summary-csv-family")
        self.assertIsNotNone(family, "Family creation failed")

        # Add members
        member1 = services.add_family_member(self.db, family.id, "Alice", age_years=30, gender=GenderEnum.FEMALE)
        member2 = services.add_family_member(self.db, family.id, "Bob", age_years=35, gender=GenderEnum.MALE, height_cm=180)
        self.assertIsNotNone(member1)
        self.assertIsNotNone(member2)

        csv_summary = services.get_family_members_summary(self.db, family.id)
        self.assertIsInstance(csv_summary, str)

        # Normalize newlines and split
        lines = csv_summary.replace('\r\n', '\n').strip().split('\n')

        self.assertEqual(len(lines), 3) # Header + 2 members
        self.assertEqual(lines[0], "id,name,height_cm,weight_kg,age_years,gender,target_caloric_intake_kcal")

        # Check content (order of members might vary, so check for presence)
        alice_line_found = any("Alice" in line and "female" in line for line in lines[1:])
        bob_line_found = any("Bob" in line and "male" in line and "180" in line for line in lines[1:])
        self.assertTrue(alice_line_found, "Alice's data not found or incorrect in CSV")
        self.assertTrue(bob_line_found, "Bob's data not found or incorrect in CSV")


    def test_get_family_members_summary_no_members(self):
        family = services.create_family(self.db, name="No Members Family", slug="no-members-family")
        self.assertIsNotNone(family, "Family creation failed")
        summary = services.get_family_members_summary(self.db, family.id)
        self.assertEqual(summary, "No members found for this family.")

    def test_get_family_members_summary_family_not_found(self):
        summary = services.get_family_members_summary(self.db, 999) # Non-existent family_id
        self.assertEqual(summary, "Family not found.")

    def test_get_family_member_details(self):
        family = services.create_family(self.db, name="Details Family", slug="details-slug")
        self.assertIsNotNone(family, "Family creation failed")
        member1 = services.add_family_member(self.db, family.id, "Detail Member", age_years=40)
        self.assertIsNotNone(member1, "Member creation failed")

        retrieved_member = services.get_family_member_details(self.db, member1.id)
        self.assertIsNotNone(retrieved_member)
        self.assertEqual(retrieved_member.name, "Detail Member")
        self.assertEqual(retrieved_member.age_years, 40)

        non_existent_member = services.get_family_member_details(self.db, 999) # Non-existent member_id
        self.assertIsNone(non_existent_member)

    # --- ShoppingListService Tests ---
    def test_create_shopping_list(self):
        family = services.create_family(self.db, name="List Test Family", slug="list-test-family")
        self.assertIsNotNone(family, "Family creation failed")
        items = {"apples": 5, "bread": 1}
        shopping_list = services.create_shopping_list(self.db, family_id=family.id, items=items)

        self.assertIsNotNone(shopping_list)
        self.assertEqual(shopping_list.family_id, family.id)
        self.assertEqual(shopping_list.items_json["apples"], 5)
        self.assertIsNotNone(shopping_list.created_at)

    def test_create_shopping_list_family_not_found(self):
        items = {"milk": 1}
        shopping_list = services.create_shopping_list(self.db, family_id=999, items=items) # Non-existent family_id
        self.assertIsNone(shopping_list)

    def test_get_latest_shopping_list(self):
        family = services.create_family(self.db, name="Latest List Family", slug="latest-list-family")
        self.assertIsNotNone(family, "Family creation failed")

        list1 = services.create_shopping_list(self.db, family.id, {"item1": "old"})
        self.assertIsNotNone(list1)

        # Introduce a delay to ensure distinct created_at timestamps
        # This is a common, if slightly imperfect, way to test "latest" in SQLite without mocking time
        import time; time.sleep(0.02) # Increased delay slightly

        list2 = services.create_shopping_list(self.db, family.id, {"item2": "new"})
        self.assertIsNotNone(list2)

        latest_list = services.get_latest_shopping_list(self.db, family.id)
        self.assertIsNotNone(latest_list)
        self.assertEqual(latest_list.id, list2.id, "The latest list should be list2")
        self.assertEqual(latest_list.items_json["item2"], "new")

    def test_get_latest_shopping_list_no_lists(self):
        family = services.create_family(self.db, name="No Lists Family", slug="no-lists-family")
        self.assertIsNotNone(family, "Family creation failed")
        latest_list = services.get_latest_shopping_list(self.db, family.id)
        self.assertIsNone(latest_list)

    def test_get_latest_shopping_list_family_not_found(self):
        latest_list = services.get_latest_shopping_list(self.db, 999) # Non-existent family_id
        self.assertIsNone(latest_list)

    def test_get_shopping_list_by_id(self):
        family = services.create_family(self.db, name="Get List By ID Family", slug="get-list-by-id-slug")
        self.assertIsNotNone(family, "Family creation failed")
        list1 = services.create_shopping_list(self.db, family.id, {"itemA": "valueA"})
        self.assertIsNotNone(list1)

        retrieved_list = services.get_shopping_list_by_id(self.db, list1.id)
        self.assertIsNotNone(retrieved_list)
        self.assertEqual(retrieved_list.items_json["itemA"], "valueA")

        non_existent_list = services.get_shopping_list_by_id(self.db, 999) # Non-existent list_id
        self.assertIsNone(non_existent_list)

if __name__ == '__main__':
    unittest.main()
