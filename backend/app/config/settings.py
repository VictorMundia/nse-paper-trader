# This imports the os module so we can read environment variables.
import os

# This imports timedelta so we can express the token lifetime as a length of time.
from datetime import timedelta

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
 # This keeps students logged in for a study day instead of the library default of 15 minutes.
 JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
 # This sets the default virtual balance for new users in Kenyan Shillings.
 STARTING_VIRTUAL_BALANCE = 100000
 # This is the frontend address used to build password reset links.
 FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
 # This is the SMTP server for sending email, e.g. smtp.gmail.com; left empty, emails are printed to the console.
 MAIL_SERVER = os.getenv("MAIL_SERVER")
 # This is the SMTP port; 587 is the standard port for STARTTLS.
 MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
 # This is the SMTP login name.
 MAIL_USERNAME = os.getenv("MAIL_USERNAME")
 # This is the SMTP password, e.g. a Gmail app password; it must only ever live in .env.
 MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
 # This is the From address on outgoing email; it defaults to the login name.
 MAIL_SENDER = os.getenv("MAIL_SENDER") or os.getenv("MAIL_USERNAME")
