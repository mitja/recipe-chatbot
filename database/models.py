import enum as py_enum # Use py_enum to avoid conflict with SQLAlchemy's Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from .database_config import Base # Import Base from the same directory

class GenderEnum(py_enum.Enum):
    MALE = "male"
    FEMALE = "female"
    DIVERSE = "diverse"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class Family(Base):
    __tablename__ = "family"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True) # Added index=True for PK for some DBs best practice
    name = Column(String(100), unique=True, nullable=False, index=True) # Added index for name as it's unique
    slug = Column(String(100), unique=True, index=True, nullable=False)

    # Relationships
    members = relationship("FamilyMember", back_populates="family", cascade="all, delete-orphan")
    shopping_lists = relationship("ShoppingList", back_populates="family", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Family(id={self.id}, name='{self.name}', slug='{self.slug}')>"

class FamilyMember(Base):
    __tablename__ = "family_member"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    family_id = Column(Integer, ForeignKey("family.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    height_cm = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    age_years = Column(Integer, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True) # Using SQLAlchemy Enum here
    target_caloric_intake_kcal = Column(Integer, nullable=True)

    # Relationship
    family = relationship("Family", back_populates="members")

    def __repr__(self):
        return f"<FamilyMember(id={self.id}, name='{self.name}', family_id={self.family_id})>"

class ShoppingList(Base):
    __tablename__ = "shopping_list"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    family_id = Column(Integer, ForeignKey("family.id"), nullable=False)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    # Using JSON type. For SQLite, this often means TEXT affinity and manual JSON handling
    # or SQLAlchemy's JSON type handling which might do the serialization/deserialization.
    items_json = Column(JSON, nullable=True) 

    # Relationship
    family = relationship("Family", back_populates="shopping_lists")

    def __repr__(self):
        return f"<ShoppingList(id={self.id}, family_id={self.family_id}, created_at='{self.created_at}')>"
