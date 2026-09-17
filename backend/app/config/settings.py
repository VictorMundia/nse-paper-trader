# This imports the os module so we can read environment variables.
import os

# This imports load_dotenv so values from a .env file can be loaded into environment variables.
from dotenv import load_dotenv

# This loads environment variables from the .env file into the process environment.
load_dotenv()

# This class stores all Flask configuration values in one place.
class Config:
 # This reads the PostgreSQL database URL from the DATABASE_URL environment variable.
 SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
 # This disables SQLAlchemy event tracking to reduce unnecessary memory usage.
 SQLALCHEMY_TRACK_MODIFICATIONS = False
 # This reads the JWT secret key from environment variables for token signing.
 JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
 # This sets the default virtual balance for new users in Kenyan Shillings.
 STARTING_VIRTUAL_BALANCE = 100000
