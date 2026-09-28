# This imports the fetch helper that returns the full HTTP response.
from app.scraper.nse_scraper import fetch_nse_response
# This imports the parser that turns the HTML table into stock rows.
from app.scraper.nse_scraper import parse_nse_table_rows
# This imports the filter that keeps only our tracked tickers.
from app.scraper.nse_scraper import filter_tracked_stocks

# This runs the test only when the file is executed directly.
if __name__ == "__main__":
    # This guards the whole test so failures print a readable message.
    try:
        # This downloads the NSE page with browser headers.
        response = fetch_nse_response()
        # This prints the HTTP status code so we can confirm a 200 response.
        print(f"Status code: {response.status_code}")
        # This parses the HTML table into structured stock rows.
        parsed_rows = parse_nse_table_rows(response.text)
        # This prints how many rows the whole table contained.
        print(f"Total rows parsed: {len(parsed_rows)}")
        # This fails the test when fewer than 5 usable rows were found.
        if len(parsed_rows) < 5:
            # This signals that parsing did not find enough data.
            raise RuntimeError(f"Expected at least 5 stock rows, got {len(parsed_rows)}.")
        # This labels the sample output section.
        print("First 5 stocks:")
        # This prints the first five parsed rows as a sanity check.
        for row in parsed_rows[:5]:
            # This shows ticker, company name and price for one stock.
            print(f"  {row['ticker']} | {row['name']} | {row['price']}")
        # This narrows the rows down to the tickers we track.
        tracked_rows = filter_tracked_stocks(parsed_rows)
        # This prints how many tracked tickers were found on the page.
        print(f"Tracked stocks matched: {len(tracked_rows)} of 15")
        # This lists each tracked stock with its current price.
        for row in tracked_rows:
            # This shows ticker and price for one tracked stock.
            print(f"  {row['ticker']} -> {row['price']}")
        # This confirms the source is reachable and parseable.
        print("NSE source is reachable and parsed successfully.")
    # This catches any failure during fetching or parsing.
    except Exception as error:
        # This prints a short failure header.
        print("NSE fetch test failed.")
        # This prints the underlying error detail for debugging.
        print(error)
