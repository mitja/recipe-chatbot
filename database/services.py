# In database/services.py

import io # Added
import csv # Added
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Dict # Added Dict (used as dict, but for clarity)

from .models import Family, FamilyMember, GenderEnum, ShoppingList # Added ShoppingList

def create_family(db: Session, name: str, slug: str) -> Optional[Family]:
    """
    Creates a new family.
    Returns the created Family object, or None if a family with the same name or slug already exists.
    """
    existing_family = db.query(Family).filter((Family.name == name) | (Family.slug == slug)).first()
    if existing_family:
        return None 
        
    new_family = Family(name=name, slug=slug)
    try:
        db.add(new_family)
        db.commit()
        db.refresh(new_family)
        return new_family
    except IntegrityError:
        db.rollback()
        return None

def get_family_by_slug(db: Session, slug: str) -> Optional[Family]:
    """
    Retrieves a family by its slug.
    Returns the Family object or None if not found.
    """
    return db.query(Family).filter(Family.slug == slug).first()

def get_family_by_id(db: Session, family_id: int) -> Optional[Family]:
    """
    Retrieves a family by its ID.
    Returns the Family object or None if not found.
    """
    return db.query(Family).filter(Family.id == family_id).first()

# --- FamilyMemberService Functions ---

def add_family_member(db: Session, family_id: int, name: str, 
                      height_cm: Optional[int] = None, 
                      weight_kg: Optional[float] = None, 
                      age_years: Optional[int] = None, 
                      gender: Optional[GenderEnum] = None, 
                      target_caloric_intake_kcal: Optional[int] = None) -> Optional[FamilyMember]:
    """
    Adds a new member to an existing family.
    Returns the created FamilyMember object, or None if the family does not exist.
    """
    family = get_family_by_id(db, family_id) # Use the existing service function
    if not family:
        return None

    new_member = FamilyMember(
        family_id=family_id,
        name=name,
        height_cm=height_cm,
        weight_kg=weight_kg,
        age_years=age_years,
        gender=gender,
        target_caloric_intake_kcal=target_caloric_intake_kcal
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

def get_family_members_summary(db: Session, family_id: int) -> str:
    """
    Retrieves all members for a given family_id and formats them as a CSV string.
    Columns: id, name, height_cm, weight_kg, age_years, gender, target_caloric_intake_kcal.
    Returns an empty string if the family is not found or has no members.
    """
    family = get_family_by_id(db, family_id) # Use the existing service function
    if not family:
        return "Family not found." # Or specific error / empty string

    members = db.query(FamilyMember).filter(FamilyMember.family_id == family_id).all()
    if not members:
        return "No members found for this family."

    output = io.StringIO()
    csv_writer = csv.writer(output)
    
    # Write header
    header = ['id', 'name', 'height_cm', 'weight_kg', 'age_years', 'gender', 'target_caloric_intake_kcal']
    csv_writer.writerow(header)
    
    # Write member data
    for member in members:
        gender_value = member.gender.value if member.gender else None # Get string value from Enum
        csv_writer.writerow([
            member.id,
            member.name,
            member.height_cm,
            member.weight_kg,
            member.age_years,
            gender_value,
            member.target_caloric_intake_kcal
        ])
        
    return output.getvalue().strip() # Use strip() to remove any trailing newline

def get_family_member_details(db: Session, member_id: int) -> Optional[FamilyMember]:
    """
    Retrieves full details for a specific family member by their ID.
    Returns the FamilyMember object or None if not found.
    """
    return db.query(FamilyMember).filter(FamilyMember.id == member_id).first()

# --- ShoppingListService Functions ---

def create_shopping_list(db: Session, family_id: int, items: Dict) -> Optional[ShoppingList]: # Changed dict to Dict
    """
    Creates a new shopping list for an existing family.
    'items' is a Python dictionary that will be stored in the JSON field.
    Returns the created ShoppingList object, or None if the family does not exist.
    """
    family = get_family_by_id(db, family_id) # Use the existing service function
    if not family:
        return None

    new_shopping_list = ShoppingList(
        family_id=family_id,
        items_json=items 
    )
    # created_at is handled by server_default=func.now() in the model
    
    db.add(new_shopping_list)
    db.commit()
    db.refresh(new_shopping_list)
    return new_shopping_list

def get_latest_shopping_list(db: Session, family_id: int) -> Optional[ShoppingList]:
    """
    Retrieves the most recent shopping list for a given family.
    Returns the ShoppingList object or None if the family has no shopping lists or does not exist.
    """
    # First, check if family exists to give a clear indication, though the query itself would also return None.
    # family = get_family_by_id(db, family_id) 
    # if not family:
    #     return None # Or raise FamilyNotFoundError

    return db.query(
            ShoppingList
        ).filter(
            ShoppingList.family_id == family_id
        ).order_by(
            ShoppingList.created_at.desc(),
            ShoppingList.id.desc()
        ).first()

def get_shopping_list_by_id(db: Session, shopping_list_id: int) -> Optional[ShoppingList]:
    """
    Retrieves a specific shopping list by its ID.
    Returns the ShoppingList object or None if not found.
    """
    return db.query(ShoppingList).filter(ShoppingList.id == shopping_list_id).first()
