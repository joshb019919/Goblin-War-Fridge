"""Create models representing tables in the database, gwf.db."""
# Import from SQLAlchemy to create in-database models
from sqlalchemy import Column
from sqlalchemy import Float

# from sqlalchemy import ForeignKeyConstraint as ForeignKey
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import PrimaryKeyConstraint as PrimaryKey
from sqlalchemy.orm import relationship
from sqlalchemy import String

# Import SQLAlchemy's declarative_base and assign to parent class Base
# Subclass Base with in-database Python models
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# USDA's FoodData Central api key, supplied as params keyword
FDC_API_KEY = "6qzVjZJSy1tnpnnCuWuyypBjvV3pHkmvUdn22HHG"


class IngredientNutrient(Base):
    __tablename__ = "ingredientNutrients"

    ingredient_id = Column("ingredientID", ForeignKey("ingredients.ingredientID"), index=True)
    nutrient_id = Column("nutrientID", ForeignKey("nutrients.nutrientID"), index=True)
    amount = Column("amount", Float(10, 2), index=True)

    nutrient = relationship("Nutrient", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="nutrients")

    PrimaryKey(ingredient_id, nutrient_id, name="ingredient_nutrient_ids")


class Nutrient(Base):
    __tablename__ = "nutrients"

    nutrient_id = Column("nutrientID", Integer(), primary_key=True, index=True)
    fdc_number = Column("fdcNumber", Integer(), nullable=False)
    name = Column("name", String(30), nullable=False)
    notes = Column("notes", String(80))

    ingredients = relationship(IngredientNutrient, back_populates="nutrient")


class Ingredient(Base):
    __tablename__ = "ingredients"

    ingredient_id = Column("ingredientID", Integer(), primary_key=True, index=True)
    fdc_id = Column("fdcID", Integer())
    name = Column("name", String(32), nullable=False)
    description = Column("description", String(1024))

    nutrients = relationship(IngredientNutrient, back_populates="ingredient")
