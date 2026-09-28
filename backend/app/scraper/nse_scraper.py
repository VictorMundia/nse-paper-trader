# This imports random so the fallback can generate small price movements.
import random

# This imports Decimal so prices keep exact currency precision.
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

# This imports BeautifulSoup so we can read the HTML table row by row.
from bs4 import BeautifulSoup

# This imports requests so we can download the NSE page over HTTP.
import requests

# This imports request exceptions so network failures can be handled cleanly.
from requests.exceptions import RequestException, Timeout

# This is the confirmed working NSE data source.
NSE_SOURCE_URL = "https://afx.kwayisi.org/nse/"

# These headers make our request look like a normal Chrome browser so the site does not block us.
REQUEST_HEADERS = {
    # This identifies the client as Chrome on Windows.
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # This tells the server which content types we accept.
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    # This tells the server our preferred language.
    "Accept-Language": "en-US,en;q=0.9",
    # This tells the server which compression formats we understand.
    "Accept-Encoding": "gzip, deflate, br",
    # This asks the server to keep the connection alive like a browser does.
    "Connection": "keep-alive",
}

# These are the only tickers we save to the database.
TRACKED_TICKERS = [
    # Safaricom PLC
    "SCOM",
    # Equity Group Holdings
    "EQTY",
    # KCB Group
    "KCB",
    # Absa Bank Kenya
    "ABSA",
    # Co-operative Bank
    "COOP",
    # East African Breweries
    "EABL",
    # BAT Kenya
    "BAT",
    # Bamburi Cement
    "BAMB",
    # Jubilee Holdings
    "JUB",
    # Nation Media Group
    "NMG",
    # Standard Chartered Kenya
    "SCBK",
    # Diamond Trust Bank
    "DTK",
    # NCBA Group
    "NCBA",
    # Stanbic Holdings
    "SBIC",
    # Centum Investment
    "CTUM",
]

# These starting prices are used only when a stock has no saved price in the database yet.
BASE_PRICES = {
    # Safaricom base price in KES.
    "SCOM": Decimal("14.90"),
    # Equity Group base price in KES.
    "EQTY": Decimal("47.00"),
    # KCB Group base price in KES.
    "KCB": Decimal("37.55"),
    # Absa Bank Kenya base price in KES.
    "ABSA": Decimal("15.30"),
    # Co-operative Bank base price in KES.
    "COOP": Decimal("14.55"),
    # East African Breweries base price in KES.
    "EABL": Decimal("180.00"),
    # BAT Kenya base price in KES.
    "BAT": Decimal("351.00"),
    # Bamburi Cement base price in KES.
    "BAMB": Decimal("66.00"),
    # Jubilee Holdings base price in KES.
    "JUB": Decimal("167.75"),
    # Nation Media Group base price in KES.
    "NMG": Decimal("13.50"),
    # Standard Chartered Kenya base price in KES.
    "SCBK": Decimal("236.00"),
    # Diamond Trust Bank base price in KES.
    "DTK": Decimal("53.00"),
    # NCBA Group base price in KES.
    "NCBA": Decimal("44.00"),
    # Stanbic Holdings base price in KES.
    "SBIC": Decimal("127.00"),
    # Centum Investment base price in KES.
    "CTUM": Decimal("10.00"),
}

# This is the largest fallback move per run: 0.015 means plus or minus 1.5%.
FALLBACK_MAX_MOVE = 0.015

# This is how many times we retry a failed request before giving up.
MAX_RETRIES = 3

# This is how long a single request attempt may take before timing out.
REQUEST_TIMEOUT_SECONDS = 30


def fetch_nse_response(source_url=NSE_SOURCE_URL):
    """Download the NSE page and return the HTTP response, retrying on network errors."""
    # This retries the request up to MAX_RETRIES times.
    for attempt in range(1, MAX_RETRIES + 1):
        # This guards a single request attempt.
        try:
            # This sends the GET request with browser headers and a timeout.
            response = requests.get(
                source_url,
                headers=REQUEST_HEADERS,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            # This raises an error if the server replied with 4xx or 5xx.
            response.raise_for_status()
            # This returns the successful response to the caller.
            return response
        # This handles the server taking too long to reply.
        except Timeout as error:
            # This only gives up on the final attempt.
            if attempt == MAX_RETRIES:
                # This converts the low-level error into a readable message.
                raise RuntimeError("NSE source timed out after multiple attempts.") from error
        # This handles connection errors and bad status codes.
        except RequestException as error:
            # This only gives up on the final attempt.
            if attempt == MAX_RETRIES:
                # This converts the low-level error into a readable message.
                raise RuntimeError("NSE source request failed after multiple attempts.") from error


def fetch_nse_page(source_url=NSE_SOURCE_URL):
    """Return the raw HTML text of the NSE page."""
    # This reuses the retrying fetch helper.
    response = fetch_nse_response(source_url)
    # This returns only the HTML body text.
    return response.text


def parse_nse_table_rows(html_text):
    """Parse the NSE price table into a list of stock dictionaries."""
    # lxml is required because the page omits closing </td>/</tr> tags, which html.parser mis-nests.
    soup = BeautifulSoup(html_text, "lxml")
    # This collects every table because the page layout may contain more than one.
    tables = soup.find_all("table")
    # This stops early when the page has no tables at all.
    if not tables:
        # This signals that the page structure was not what we expected.
        raise RuntimeError("No HTML table was found on the NSE page.")

    # This holds every valid stock row we manage to parse.
    parsed_records = []
    # This checks each table until one yields usable rows.
    for table in tables:
        # This walks through every row of the current table.
        for row in table.find_all("tr"):
            # This grabs the data cells, which excludes header cells.
            cells = row.find_all("td")
            # This skips rows that do not have the expected five columns.
            if len(cells) < 5:
                # This moves on to the next row.
                continue
            # Column 0 holds the ticker symbol.
            ticker = cells[0].get_text(strip=True).upper()
            # Column 1 holds the company name.
            company_name = cells[1].get_text(strip=True)
            # Column 2 holds the traded volume, which may be empty.
            volume_value = _parse_int(cells[2].get_text(strip=True))
            # Column 3 holds the price.
            price_value = _parse_decimal(cells[3].get_text(strip=True))
            # Column 4 holds the daily change, which may be empty.
            change_value = _parse_decimal(cells[4].get_text(strip=True))
            # This skips rows without a ticker or without a usable price.
            if not ticker or price_value is None:
                # This moves on to the next row.
                continue
            # This stores one clean stock record.
            parsed_records.append(
                {
                    # The NSE ticker symbol.
                    "ticker": ticker,
                    # The company display name.
                    "name": company_name,
                    # The traded volume, or None when the cell was empty.
                    "volume": volume_value,
                    # The current price as a Decimal.
                    "price": price_value,
                    # The daily change, or None when the cell was empty.
                    "change": change_value,
                }
            )
        # This stops once a table has produced usable rows.
        if parsed_records:
            # This avoids parsing unrelated tables further down the page.
            break

    # This returns every row we successfully parsed.
    return parsed_records


def filter_tracked_stocks(parsed_records):
    """Keep only the rows whose ticker is in our tracked list."""
    # This uses a set for fast membership checks.
    tracked = set(TRACKED_TICKERS)
    # This returns only the rows we care about saving.
    return [record for record in parsed_records if record["ticker"] in tracked]


def get_last_saved_price(stock):
    """Return the most recent close price saved for a stock, or None if it has none."""
    # This import is local to avoid a circular import at module load time.
    from app.models.price import Price

    # This returns None straight away for stocks that are not in the database yet.
    if stock is None:
        # This signals that no saved price exists.
        return None
    # This fetches the newest price row for this stock.
    latest_row = (
        # This starts a query on the prices table.
        Price.query
        # This limits the query to this one stock.
        .filter_by(stock_id=stock.id)
        # This puts the newest row first.
        .order_by(Price.recorded_at.desc())
        # This takes only that newest row.
        .first()
    )
    # This returns the saved price, or None when the stock has no price rows.
    return latest_row.close_price if latest_row else None


def simulate_next_price(last_price):
    """Apply a random move of up to plus or minus 1.5% to the last known price."""
    # This picks a random multiplier between 0.985 and 1.015.
    multiplier = 1 + random.uniform(-FALLBACK_MAX_MOVE, FALLBACK_MAX_MOVE)
    # This converts the multiplier to Decimal via text so no float error leaks into the price.
    new_price = Decimal(last_price) * Decimal(str(multiplier))
    # This rounds to 2 decimal places like a real KES share price.
    return new_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def run_full_scrape_once(source_url=NSE_SOURCE_URL):
    """Save one price per tracked stock, using live data where possible and the fallback otherwise."""
    # This import is local to avoid a circular import at module load time.
    from app.extensions import db
    # This import is local to avoid a circular import at module load time.
    from app.models.stock import Stock
    # This import is local to avoid a circular import at module load time.
    from app.models.price import Price

    # This tries the live website first.
    try:
        # This downloads the page HTML.
        html_text = fetch_nse_page(source_url)
        # This turns the HTML table into structured rows.
        parsed_records = parse_nse_table_rows(html_text)
    # This catches a site that is down, blocked, or has changed its layout.
    except RuntimeError as error:
        # This explains in the console why we are switching to the fallback.
        print(f"Live NSE fetch failed, using fallback prices: {error}")
        # This leaves no live rows so every ticker uses the fallback.
        parsed_records = []

    # This keeps only the tickers we track and indexes them by ticker for quick lookup.
    live_by_ticker = {record["ticker"]: record for record in filter_tracked_stocks(parsed_records)}

    # This counts brand-new stock master rows.
    new_stocks_created = 0
    # This counts inserted price rows.
    price_rows_saved = 0
    # This remembers which tickers had to use the simulated price.
    fallback_tickers = []

    # This goes through every tracked ticker so all 15 always get a price.
    for ticker in TRACKED_TICKERS:
        # This looks for an existing stock with the same ticker.
        stock = Stock.query.filter_by(ticker=ticker).first()
        # This uses the live row when the website returned this ticker.
        if ticker in live_by_ticker:
            # This takes the scraped row as-is.
            record = live_by_ticker[ticker]
        else:
            # This starts from the last saved price, or the base price if none exists.
            last_price = get_last_saved_price(stock) or BASE_PRICES[ticker]
            # This builds a record shaped like a scraped row, using the simulated price.
            record = {
                # The NSE ticker symbol.
                "ticker": ticker,
                # The saved company name, or the ticker if the stock is brand new.
                "name": stock.company_name if stock else ticker,
                # There is no real volume for a simulated price.
                "volume": None,
                # The last price moved by up to plus or minus 1.5%.
                "price": simulate_next_price(last_price),
                # The simulated change is not recorded.
                "change": None,
            }
            # This records that this ticker used the fallback.
            fallback_tickers.append(ticker)

        # This creates the stock master row the first time we see the ticker.
        if stock is None:
            # This builds the new stock record.
            stock = Stock(
                # This stores the ticker symbol.
                ticker=record["ticker"],
                # This stores the company name, falling back to the ticker.
                company_name=record["name"] or record["ticker"],
                # The source table has no sector column, so this stays empty.
                sector=None,
                # This labels the exchange as NSE.
                market="NSE",
                # This marks the stock as tradable in the simulator.
                is_active=True,
            )
            # This stages the new stock for insertion.
            db.session.add(stock)
            # This assigns stock.id so the price row can reference it.
            db.session.flush()
            # This records that a new stock was created.
            new_stocks_created += 1
        else:
            # This refreshes the stored company name from the live source.
            stock.company_name = record["name"] or stock.company_name

        # This creates the price snapshot for this scrape run.
        price_row = Price(
            # This links the price to its stock.
            stock_id=stock.id,
            # This stores the scraped price as the closing price.
            close_price=record["price"],
            # This stores the traded volume when the source provided one.
            volume=record["volume"],
        )
        # This stages the price row for insertion.
        db.session.add(price_row)
        # This records that a price row was saved.
        price_rows_saved += 1

    # This writes every staged change in a single transaction.
    db.session.commit()

    # This labels the run: all live, all simulated, or a mix of both.
    if not fallback_tickers:
        # Every price came from the website.
        source = "live"
    elif len(fallback_tickers) == len(TRACKED_TICKERS):
        # Every price was simulated.
        source = "fallback"
    else:
        # Some prices were live and some were simulated.
        source = "mixed"
    # This prints the outcome so it shows up in the server console.
    print(f"Scrape finished: source={source}, fallback tickers={fallback_tickers or 'none'}")

    # This returns counts so callers can log the outcome.
    return {
        # Whether this run used live, fallback, or mixed data.
        "source": source,
        # Which tickers used the simulated price.
        "fallback_tickers": fallback_tickers,
        # How many rows the whole table contained.
        "total_rows_parsed": len(parsed_records),
        # How many tracked stocks received a price this run.
        "stocks_processed": len(TRACKED_TICKERS),
        # How many new stock master rows were created.
        "new_stocks_created": new_stocks_created,
        # How many price rows were inserted.
        "price_rows_saved": price_rows_saved,
    }


def _parse_decimal(raw_text):
    """Convert scraped text into a Decimal, or None when it is not a number."""
    # This strips commas, currency prefixes and plus signs.
    cleaned = _clean_numeric_text(raw_text)
    # This treats empty cells as missing values.
    if not cleaned:
        # This signals that no number was present.
        return None
    # This guards against text that is not numeric at all.
    try:
        # This converts via string so decimal digits stay exact.
        return Decimal(cleaned)
    # This catches values like "-" or "N/A".
    except (InvalidOperation, ValueError):
        # This signals that conversion failed.
        return None


def _parse_int(raw_text):
    """Convert scraped text into an integer, or None when it is not a number."""
    # This strips commas, currency prefixes and plus signs.
    cleaned = _clean_numeric_text(raw_text)
    # This treats empty cells as missing values.
    if not cleaned:
        # This signals that no number was present.
        return None
    # This guards against text that is not numeric at all.
    try:
        # This parses as float first so values like "1300.0" still work.
        return int(float(cleaned))
    # This catches values like "-" or "N/A".
    except ValueError:
        # This signals that conversion failed.
        return None


def _clean_numeric_text(raw_text):
    """Remove currency symbols, separators and signs from scraped numeric text."""
    # This guarantees we always work with a string.
    text_value = str(raw_text or "")
    # This removes surrounding whitespace.
    text_value = text_value.strip()
    # This removes thousand separators.
    text_value = text_value.replace(",", "")
    # This removes the KES currency prefix.
    text_value = text_value.replace("KES", "")
    # This removes the KSh currency prefix.
    text_value = text_value.replace("KSh", "")
    # This removes the leading plus sign used on positive changes.
    text_value = text_value.replace("+", "")
    # This returns the cleaned numeric candidate.
    return text_value.strip()
