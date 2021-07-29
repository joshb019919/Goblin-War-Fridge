"""Goblin War Fridge.

SOURCES/CREDITS:

I learned a great deal from SQLAlchemy tutoriral + related websites
https://docs.sqlalchemy.org/en/14/orm/session_basics.html
https://docs.sqlalchemy.org/en/14/orm/session_transaction.html
https://docs.sqlalchemy.org/en/14/orm/tutorial.html
https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html

Also, thanks to the following website
https://www.pythoncentral.io/understanding-python-sqlalchemy-session/

DOCUMENTATION:
Found in DOCSTRING.txt and README.md

YOUTUBE LINK TO INTRODUCTORY VIDEO:
https://youtu.be/iGxR5bruMTY
"""
# Tools:
# os for exporting "development server" to command line
# requests for getting http data from USDA's FoodData Central API
import os
import requests

# Tools for the Flask application
from flask import Flask
from flask import render_template as render
from flask import request
from flask import session

# For using file directory rather than signed cookies
from tempfile import mkdtemp

# From internal config.py file
from models import FDC_API_KEY
from models import Ingredient
from models import IngredientNutrient
from models import Nutrient

# For generating engine and session factories for database access
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Main Flask app and 'development server' pushed to the environment
app = Flask(__name__)
os.environ["FLASK_ENV"] = "development"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = FDC_API_KEY

# Connect to a simple SQLite database
SQLALCHEMY_DATABASE_URI = "sqlite:///gwf.db"

# Create SQLAlchemy engine(s) to be used in database sessions
engine = create_engine(SQLALCHEMY_DATABASE_URI,
                       connect_args={"check_same_thread": False})

# Session factory to generate session(s) for connecting to the database
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@app.route("/", methods=["GET", "POST"])
def index():
    """Warrior requests food information."""
    if request.method == "POST":

        # Use the inputted food item to search the FoodData Central
        # database for appropriate food items
        food = request.form.get("food")
        url = "https://api.nal.usda.gov/fdc/v1/foods/list"
        params = {"api_key": FDC_API_KEY,
                  "dataType": ["Foundation"],
                  "query": food}

        # Use requests library to get the data from FDC
        # Check to make sure it worked
        session["json_response"] = requests.get(url, params=params).json()
        if not session["json_response"]:
            return render("index.jinja.html", no=True)

        # Generate a selection of exact foods within the db for which
        # to search; check to make sure it worked
        options = [food["description"] for food in session["json_response"]]
        if not options:
            return render("index.jinja.html", no=True)

        return render(
            "selection.jinja.html",
            data=session["json_response"],
            query=food,
            options=options)

    else:
        return render("index.jinja.html")


@app.route("/food", methods=["POST"])
def food():
    # Get the exact name of the food for which to search, and make a
    # second search for only that food
    desc = request.form.get("returned_foods")

    url = "https://api.nal.usda.gov/fdc/v1/foods/list"
    params = {"api_key": FDC_API_KEY,
              "dataType": ["Foundation", "SR Legacy", "FNDDS"],
              "query": desc}

    # Let's hope the first item is always the one we wanted, otherwise
    # it returns every item from the list, not just what we searched
    session["food"] = requests.get(url, params=params).json()[0]

    # Separate each value for forming the insertable database model
    name = session["food"]["description"]
    fdc_id = session["food"]["fdcId"]
    food = session["food"]
    nutrients = food["foodNutrients"]

    # List of nutrient numbers to track
    nut_ids = ["203", "204", "208", "209", "291", "307"]

    # Use tracked nut_ids to only get the nutrient data needed
    nuts = {"name": name}

    # Manually enter each tracked nutrient into the nuts dictionary
    # Don't know a better way to do this
    _ = [nut["amount"] for nut in nutrients if nut["number"] == "208"]
    if len(_) > 0:
        nuts["calories"] = _[0]
    else:
        nuts["calories"] = 0

    _ = [nut["amount"] for nut in nutrients if nut["number"] == "204"]
    if len(_) > 0:
        nuts["total_fat"] = _[0]
    else:
        nuts["total_fat"] = 0

    _ = [nut["amount"] for nut in nutrients if nut["number"] == "203"]
    if len(_) > 0:
        nuts["protein"] = _[0]
    else:
        nuts["protein"] = 0

    _ = [nut["amount"] for nut in nutrients if nut["number"] == "307"]
    if len(_) > 0:
        nuts["sodium"] = _[0]
    else:
        nuts["sodium"] = 0

    _ = [nut["amount"] for nut in nutrients if nut["number"] == "291"]
    if len(_) > 0:
        nuts["fiber"] = _[0]
    else:
        nuts["fiber"] = 0

    _ = [nut["amount"] for nut in nutrients if nut["number"] == "209"]
    if len(_) > 0:
        nuts["starch"] = _[0]
    else:
        nuts["starch"] = 0

    # Form the database model to be inserted
    ingredient = Ingredient(name=name, fdc_id=fdc_id)

    # Form each nutrient as IngredientNutrient objects to be added to
    # the ingredient's relationship
    cal = IngredientNutrient(amount=nuts["calories"])
    fat = IngredientNutrient(amount=nuts["total_fat"])
    sodium = IngredientNutrient(amount=nuts["sodium"])
    fiber = IngredientNutrient(amount=nuts["fiber"])
    starch = IngredientNutrient(amount=nuts["starch"])
    protein = IngredientNutrient(amount=nuts["protein"])

    # Make one call to get all the objects in the nutrients table;
    # since only the six nutrients are tracked, this works, for now
    nutrient_table = get_table(Nutrient)

    # Assign each IngredientNutrient model with the collected nutrients
    # As the nutrients are never altered by users, this feels robust
    cal.nutrient = nutrient_table[0]        # calories row, and so on
    fat.nutrient = nutrient_table[1]        # total fat
    sodium.nutrient = nutrient_table[2]     # sodium
    fiber.nutrient = nutrient_table[3]      # fiber
    starch.nutrient = nutrient_table[4]     # starch
    protein.nutrient = nutrient_table[5]    # protein

    # Append each collected and assigned nutrient to the ingredient's
    # nutrients relationship
    ingredient.nutrients.append(cal)
    ingredient.nutrients.append(fat)
    ingredient.nutrients.append(sodium)
    ingredient.nutrients.append(fiber)
    ingredient.nutrients.append(starch)
    ingredient.nutrients.append(protein)

    # If the ingredient hasn't already been added, add it to the db
    if not get_row_by_name(Ingredient, name):
        insert(ingredient)

    return render("data.jinja.html", data=nuts)


# Helper functions for accessing the database when necessary, rather
# than globally at the top of the script
def insert(table):
    """Add items to the database."""
    with Session.begin() as s:
        s.add(table)


def get_table(Table):
    """Query whole tables from the database."""
    with Session() as s:
        return s.query(Table).all()


def get_row_by_name(Table, filter_spec):
    """Query rows from database tables."""
    with Session() as s:
        return s.query(Table).filter(Table.name==filter_spec).first()


if __name__ == "__main__":
    # USAGE: python app.py
    # -or-
    # "flask run" from the terminal
    Flask.run(app)
