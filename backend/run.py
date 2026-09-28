# This imports the app factory function that builds and configures our Flask application.
from app import create_app

# This imports the function that starts the background NSE price scheduler.
from app.scraper.scheduler import start_scheduler

# This single switch controls debug mode for both Flask and the scheduler guard.
DEBUG = True

# This creates one configured Flask app instance by calling our factory function.
app = create_app()

# This checks whether this file is being run directly from the terminal.
if __name__ == "__main__":
    # This starts the scheduler, which scrapes once now and then every 30 minutes in market hours.
    start_scheduler(app, debug=DEBUG)
    # This starts the Flask development server on localhost with the same debug setting.
    app.run(host="127.0.0.1", port=5000, debug=DEBUG)