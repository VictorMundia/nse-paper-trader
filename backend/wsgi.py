# This is the entry point for a production server such as gunicorn: gunicorn wsgi:app
from app import create_app

# This imports the scheduler that scrapes NSE prices.
from app.scraper.scheduler import start_scheduler

# This builds the Flask app from backend/.env or the host's environment variables.
app = create_app()

# This starts the price scraper; run gunicorn with one worker so it starts only once.
start_scheduler(app)
