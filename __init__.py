from app import engine
from models import Base

# Create the database gwf.db from Python class models using SQLAlchemy
# declarative_base and ORM
Base.metadata.create_all(bind=engine)
