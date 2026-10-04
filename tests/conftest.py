"""Shared test setup: a separate test database, a clean slate for every test, and helpers."""
# This imports datetime tools so test prices get increasing timestamps.
from datetime import datetime, timedelta
# This imports Decimal for exact prices.
from decimal import Decimal

# This imports pytest, the test runner.
import pytest
# This imports SQLAlchemy tools to create the test database.
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

# This imports the app factory and the real settings.
from app import create_app
from app.config.settings import Config
# This imports the shared database object.
from app.extensions import db
# This imports the models used to seed test data.
from app.models.price import Price
from app.models.stock import Stock

# These are the stocks and prices every test starts with.
SEED_PRICES = {"SCOM": "36.55", "KCB": "92.50", "BAT": "559.00"}
# This is the password used for every test account.
TEST_PASSWORD = "TestPass123!"


@pytest.fixture(scope="session")
def app():
    """Build the app against nse_paper_trader_test, never the real database."""
    # This takes the real database address and changes only the database name.
    real_url = make_url(Config.SQLALCHEMY_DATABASE_URI)
    # This is e.g. nse_paper_trader_test.
    test_url = real_url.set(database=f"{real_url.database}_test")
    # Safety net: refuse to run if the name ever stops ending in _test, because tests drop every table.
    assert test_url.database.endswith("_test"), "Refusing to run tests against a non-test database."
    # This connects to the built-in postgres database to create the test database if needed.
    admin = create_engine(real_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    # This opens the admin connection.
    with admin.connect() as conn:
        # This checks whether the test database already exists.
        exists = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": test_url.database}).scalar()
        # This creates it on the first run.
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{test_url.database}"'))
    # This closes the admin connection.
    admin.dispose()
    # This builds the app with the test database; MAIL_SERVER=None keeps emails in console mode.
    test_app = create_app({"SQLALCHEMY_DATABASE_URI": test_url.render_as_string(hide_password=False), "TESTING": True, "MAIL_SERVER": None})
    # This opens an app context for the whole test session.
    with test_app.app_context():
        # This starts from empty tables.
        db.drop_all()
        # This creates every table from the models.
        db.create_all()
        # This hands the app to the tests.
        yield test_app
        # This tidies up after the last test.
        db.session.remove()
        # This leaves the test database empty.
        db.drop_all()


@pytest.fixture(autouse=True)
def clean_database(app):
    """Give every test the same starting data, then wipe it afterwards."""
    # This seeds the three test stocks with one price each.
    for ticker, price in SEED_PRICES.items():
        # This creates the stock.
        stock = Stock(ticker=ticker, company_name=f"{ticker} Test Plc", market="NSE", is_active=True)
        # This stages it.
        db.session.add(stock)
        # This assigns stock.id.
        db.session.flush()
        # This gives it a starting price.
        db.session.add(Price(stock_id=stock.id, close_price=Decimal(price), volume=1000, recorded_at=datetime.utcnow() - timedelta(hours=1)))
    # This saves the seed data.
    db.session.commit()
    # This runs the test.
    yield
    # This discards anything the test left in the session.
    db.session.remove()
    # TRUNCATE ... CASCADE empties every table and resets ID counters in one statement.
    table_names = ", ".join(f'"{table.name}"' for table in db.metadata.sorted_tables)
    # This runs the wipe.
    db.session.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))
    # This saves the wipe.
    db.session.commit()


@pytest.fixture
def client(app):
    """A fake browser that sends requests straight to Flask, with no real server needed."""
    # This returns Flask's built-in test client.
    return app.test_client()


def register_and_login(client, email="student@example.com", full_name="Test Student", level="beginner"):
    """Create an account and return an Authorization header for it."""
    # This registers the account.
    response = client.post("/api/auth/register", json={"full_name": full_name, "email": email, "password": TEST_PASSWORD, "experience_level": level})
    # This fails the test immediately if registration did not work.
    assert response.status_code == 201, response.get_json()
    # This logs in.
    token = client.post("/api/auth/login", json={"email": email, "password": TEST_PASSWORD}).get_json()["access_token"]
    # This returns the header the API expects.
    return {"Authorization": f"Bearer {token}"}


def set_price(ticker, price):
    """Record a new, newer price for a stock, as if the scraper had just run."""
    # This finds the stock.
    stock = Stock.query.filter_by(ticker=ticker).one()
    # This saves the new price with the current time, newer than the seed price.
    db.session.add(Price(stock_id=stock.id, close_price=Decimal(price), recorded_at=datetime.utcnow()))
    # This saves it.
    db.session.commit()
