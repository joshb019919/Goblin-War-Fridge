# Goblin War Fridge
Go to war with your general lack of nutrition knowledge.

Goblin = not mainstream

LOGIN SYSTEM NOT YET IMPLEMENTED

Right now, all I have implemented is the means to search the USDA's
FoodData Central database for food items, select the proper choice
(because they have a ton) from a dropdown menu, and view the following
nutrition data on that item:

calories
total fat
sodium
fiber
starch
protein

#### USAGE: python app.py
#### -or-
#### "flask run" from the terminal


#### YouTube URL
https://youtu.be/iGxR5bruMTY

#### Apparently, the description is not nearly long enough, so I'll
#### include the other SQLAlchemy models I intend to include with a
#### future update.

class Warrior(Base):
    __tablename__ = "warriors"

    warrior_id = Column("warriorID", Integer(), primary_key=True)
    display = Column("displayName", String(30))
    goal = Column("goal", String(1024))

    registered_on = Column("registeredOn", DateTime(), default=LOG_TIME)
    updated_on = Column("updatedOn", DateTime(), onupdate=LOG_TIME)
    last_logged_on = Column("lastLoggedOn",
                            DateTime(),
                            default=LOG_TIME,
                            onupdate=LOG_TIME)


class WarriorIngredient(Base):
    __tablename__ = "warriorIngredients"

    warrior_id = Column("warriorID", Integer())
    ingredient_id = Column("ingredientID", Integer())

    PrimaryKey(warrior_id, ingredient_id, name="warrior_ingredient_ids")

    ForeignKey(["warriorID", "ingredientID"],
               ["warriors.warriorID", "meals.mealID"],
               onupdate="CASCADE")

class MealIngredient(Base):
    """MealIngredients(Base) -> dict[str, any]

    Junction table between the meals and ingredients tables.

    Allows each table a one-to-many relationship with this third table
    containing each meal's nutrients.

    Primary Keys
    ------------
    meal_id : int
    ingredient_id : int

    Foreign Keys
    ------------
    meal_id : int
        References meals.mealID
    ingredient_id : int
        References ingredients.ingredientID

    Column Attribute
    ----------------
    ingredient_amount: int
        Unit amount of an ingredient in a meal
    """
    __tablename__ = "mealIngredients"

    meal_id = Column("mealID", Integer())
    ingredient_id = Column("ingredientID", Integer())
    ingredient_amount = Column("ingredientAmount", Integer(), nullable=False)

    PrimaryKey(meal_id, ingredient_id, name="meal_ingredient_ids")

    ForeignKey(["mealID", "ingredientID"],
               ["meals.mealID", "ingredients.ingredientID"],
               onupdate="CASCADE")

    def __repr__(self):
        return f"\n\nMealIngredient\n" + \
               f"MealID:\t\t\t{self.meal_id}\n" + \
               f"IngredientID:\t\t{self.ingredient_id}\n" + \
               f"Ingredient Amount:\t{self.ingredient_amount}\n\n"
               class Meal(Base):
    """Meal(Base) -> dict[str, any]

    Meals have one or more ingredients, and many warriors can use the
    same meal.

    Meals are assemblies of the ingredients of which they are composed.
    If a warrior deselects a meal, it remains in the database to be
    viewed and learned from by other warriors.

    Special values are assembled in views, such as daily calorie
    intake.

    Primary Key
    -----------
    meal_id : int

    Column Attribute
    ----------------
    name : str
        Name of the meal; max 64 characters

    Relationship Attributes
    -----------------------
    ingredient_amounts : SQLAlchemy relationship
        amount of each food ingredient in the meal
    """
    __tablename__ = "meals"

    meal_id = Column("mealID", Integer(), primary_key=True)
    meal_name = Column("meal_name", String(64), nullable=False)

    ingredient_amounts = relationship("mealIngredients", backref="ingredient_amount")

    def __repr__(self):
        return f"\n\nMeal\n" + \
               f"MealID:\t{self.meal_id}\n" + \
               f"Name:\t{self.meal_name}\n\n"

class WarriorCredentials(Base):
    """WarriorCredentials(Base) -> dict[str, any]

    Store each warrior's email and password hash separately so extra
    security measures can be localized.

    Finds a warrior's credentials by the constraint key, warrior_id.

    Primary Key
    -----------
    warrior_id : int

    Foreign Key
    -----------
    warrior_id : int
        References warriors.warriorID

    Column Attributes
    -----------------
    email : str
        Warrior's email address for loggin in; max 64 characters
    password_hash : str
        Hash of plain text password string; max 32 characters
    """
    __tablename__ = "warriorCredentials"

    warrior_id = Column("warriorID", Integer(), primary_key=True)
    email = Column("email", String(64), nullable=False, index=True)
    password_hash = Column("passwordHash",
                           String(),
                           nullable=False,
                           index=True)

    ForeignKey(["warrior_id"], ["warriors.warriorID"], onupdate="CASCADE")

    # Remove for production
    def __repr__(self):
        return f"\n\nWarriorCredential\n" + \
               f"WarriorID:\t\t{self.warrior_id}\n" + \
               f"Hash:\t\t{self.password_hash}\n" + \
               f"Email:\t\t{self.email}\n\n"

class WarriorMeal(Base):
    """WarriorMeal(Base) -> dict[str, any]

    Junction table between the warriors and meals tables.

    Allows each table a one-to-many relationship with a third
    table containing each warrior's selected meals.

    Primary Keys
    ------------
    warrior_id : int
    meal_id : int

    Foreign Keys
    ------------
    warrior_id : int
        References warriors.warriorID
    meal_id : int
        References meals.mealID

    Relationship Attributes
    -----------------

    """
    __tablename__ = "warriorMeals"

    warrior_id = Column("warriorID", Integer())
    meal_id = Column("mealID", Integer())

    PrimaryKey(warrior_id, meal_id, name="warrior_meal_ids")

    ForeignKey(["warriorID", "mealID"],
               ["warriors.warriorID", "meals.mealID"],
               onupdate="CASCADE")

    # Implement a relationship to a table containing the nutrient value
    # and total nutritional content (maybe 2?)

    def __repr__(self):
        return f"\n\n\nWarriorMeal\n" + \
               f"WarriorID:\t{self.warrior_id}\n" + \
               f"MealID:\t\t{self.meal_id}\n\n\n"

