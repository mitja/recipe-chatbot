import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Adjust path to import from the root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.models import Family, FamilyMember, ShoppingList, GenderEnum
from database.database_config import Base # To create tables for in-memory DB

class TestDatabaseModels(unittest.TestCase):

    def setUp(self):
        # Use an in-memory SQLite database for testing
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine) # Create all tables from Base
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.SessionLocal()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine) # Drop all tables

    def test_create_family(self):
        family = Family(name="The Test Family", slug="test-family")
        self.session.add(family)
        self.session.commit()
        self.session.refresh(family)

        self.assertIsNotNone(family.id)
        self.assertEqual(family.name, "The Test Family")
        self.assertEqual(family.slug, "test-family")

    def test_create_family_member(self):
        family = Family(name="The Member Family", slug="member-family")
        self.session.add(family)
        self.session.commit()
        self.session.refresh(family)

        member = FamilyMember(
            family_id=family.id,
            name="John Doe",
            height_cm=180,
            weight_kg=75.5,
            age_years=30,
            gender=GenderEnum.MALE,
            target_caloric_intake_kcal=2500
        )
        self.session.add(member)
        self.session.commit()
        self.session.refresh(member)

        self.assertIsNotNone(member.id)
        self.assertEqual(member.name, "John Doe")
        self.assertEqual(member.family_id, family.id)
        self.assertEqual(member.gender, GenderEnum.MALE)
        
        # Test relationship from family
        self.session.refresh(family) # Refresh family to load members relationship
        self.assertIn(member, family.members)
        self.assertEqual(member.family, family)


    def test_create_shopping_list(self):
        family = Family(name="The Shopping Family", slug="shopping-family")
        self.session.add(family)
        self.session.commit()
        self.session.refresh(family)

        items_data = {"milk": "1 gallon", "eggs": "1 dozen"}
        shopping_list = ShoppingList(
            family_id=family.id,
            items_json=items_data
        )
        self.session.add(shopping_list)
        self.session.commit()
        self.session.refresh(shopping_list)

        self.assertIsNotNone(shopping_list.id)
        self.assertIsNotNone(shopping_list.created_at)
        self.assertEqual(shopping_list.family_id, family.id)
        self.assertEqual(shopping_list.items_json["milk"], "1 gallon")

        # Test relationship from family
        self.session.refresh(family) # Refresh family to load shopping_lists relationship
        self.assertIn(shopping_list, family.shopping_lists)
        self.assertEqual(shopping_list.family, family)

    def test_family_member_optional_fields(self):
        family = Family(name="Optional Fields Family", slug="optional-family")
        self.session.add(family)
        self.session.commit()
        self.session.refresh(family)

        member = FamilyMember(
            family_id=family.id,
            name="Jane Minimal"
            # All other fields are nullable (height, weight, age, gender, caloric_intake)
        )
        self.session.add(member)
        self.session.commit()
        self.session.refresh(member)

        self.assertIsNotNone(member.id)
        self.assertEqual(member.name, "Jane Minimal")
        self.assertIsNone(member.height_cm)
        self.assertIsNone(member.weight_kg)
        self.assertIsNone(member.age_years)
        self.assertIsNone(member.gender)
        self.assertIsNone(member.target_caloric_intake_kcal)


if __name__ == '__main__':
    unittest.main()
