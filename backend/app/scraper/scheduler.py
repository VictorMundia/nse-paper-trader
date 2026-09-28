# This imports atexit so we can stop the scheduler cleanly when the app shuts down.
import atexit

# This imports os so we can read the environment variable Flask's reloader sets.
import os

# This imports the scheduler that runs jobs on a background thread beside Flask.
from apscheduler.schedulers.background import BackgroundScheduler

# This imports the cron trigger so we can say "weekdays, every 30 minutes, 09:00-15:30".
from apscheduler.triggers.cron import CronTrigger

# This imports the shared database object so we can undo a failed transaction.
from app.extensions import db

# This imports the function that fetches and saves one round of prices.
from app.scraper.nse_scraper import run_full_scrape_once

# This is the NSE's local timezone (EAT, UTC+3), so the schedule ignores the laptop's clock settings.
NSE_TIMEZONE = "Africa/Nairobi"


def run_scrape_job(app):
    """Run one scrape inside the Flask app context and never let an error escape."""
    # This gives the background thread access to the database configuration.
    with app.app_context():
        # This protects the scheduler from crashing if one scrape fails.
        try:
            # This fetches prices (live or fallback) and saves them.
            summary = run_full_scrape_once()
            # This prints a one-line result in the server console.
            print(f"[Scheduler] Saved {summary['price_rows_saved']} prices (source={summary['source']}).")
        # This catches any unexpected error, e.g. the database being offline.
        except Exception as error:
            # This undoes any half-finished database changes from the failed run.
            db.session.rollback()
            # This prints the error so we can see what went wrong.
            print(f"[Scheduler] Scrape failed: {error}")


def start_scheduler(app, debug=False):
    """Start the background scheduler with a startup scrape and a market-hours schedule."""
    # In debug mode Flask runs a watcher process and a server process; only the server has this set to "true".
    if debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        # This skips the watcher process so scrapes are not duplicated.
        return None

    # This creates the scheduler and makes every job use Nairobi time.
    scheduler = BackgroundScheduler(timezone=NSE_TIMEZONE)

    # This adds a one-off job with no run date, which means "run immediately".
    scheduler.add_job(
        # This is the function the job will call.
        func=run_scrape_job,
        # This "date" trigger runs the job a single time.
        trigger="date",
        # This passes the Flask app into run_scrape_job.
        args=[app],
        # This names the job so it is easy to spot in logs.
        id="nse_startup_scrape",
    )

    # This adds the recurring job for market hours.
    scheduler.add_job(
        # This is the function the job will call.
        func=run_scrape_job,
        # This builds the market-hours schedule.
        trigger=CronTrigger(
            # This limits runs to Monday through Friday.
            day_of_week="mon-fri",
            # This allows the hours 09 to 15, which with the minutes below ends at 15:30.
            hour="9-15",
            # This runs on the hour and at half past.
            minute="0,30",
            # This interprets the times above as Nairobi time.
            timezone=NSE_TIMEZONE,
        ),
        # This passes the Flask app into run_scrape_job.
        args=[app],
        # This names the job so it is easy to spot in logs.
        id="nse_market_scrape",
        # This prevents a slow scrape from overlapping with the next one.
        max_instances=1,
        # This merges several missed runs (e.g. after the laptop sleeps) into one.
        coalesce=True,
        # This still runs a job that is up to 5 minutes late instead of skipping it.
        misfire_grace_time=300,
    )

    # This starts the background thread that runs the jobs.
    scheduler.start()
    # This stops the scheduler when Python exits, but only if nothing has stopped it already.
    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)
    # This shows when the next market-hours scrape will happen.
    print(f"[Scheduler] Started. Next market scrape: {scheduler.get_job('nse_market_scrape').next_run_time}")
    # This returns the scheduler so callers can inspect or stop it.
    return scheduler
