# This imports the app factory so we can open a Flask application context.
from app import create_app

# This imports the one-shot scraper function that fetches, parses, and saves rows.
from app.scraper.nse_scraper import run_full_scrape_once

# This checks whether this script is being run directly from terminal.
if __name__ == "__main__":
    # This creates a configured Flask app instance.
    app = create_app()
    # This opens app context so database session operations can run safely.
    with app.app_context():
        # This runs one full scrape cycle and gets summary counts.
        summary = run_full_scrape_once()
        # This prints how many stock rows were processed from source table.
        print(f"Stocks processed: {summary['stocks_processed']}")
        # This prints how many new stock master rows were created.
        print(f"New stocks created: {summary['new_stocks_created']}")
        # This prints how many price rows were saved in this run.
        print(f"Price rows saved: {summary['price_rows_saved']}")
