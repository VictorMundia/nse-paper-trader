"""Tests for the NSE scraper: HTML parsing, the random-walk fallback, and saving prices."""
# This imports Decimal for exact price checks.
from decimal import Decimal

# This imports the scraper functions under test.
from app.models.price import Price
from app.models.stock import Stock
from app.scraper.nse_scraper import (
    FALLBACK_MAX_MOVE,
    TRACKED_TICKERS,
    filter_tracked_stocks,
    parse_nse_table_rows,
    run_full_scrape_once,
    simulate_next_price,
)

# This copies the real site's style: no closing </td> or </tr> tags, plus a 3-column table that must be ignored.
SAMPLE_HTML = """
<table><thead><tr><th colspan=3>Top Gainers<tbody>
<tr><td>SKL<td>17.40<td>+5.78%
</table>
<table><thead><tr><th>Ticker<th>Name<th>Volume<th>Price<th>Change<tbody>
<tr><td><a href="#">ABSA</a><td><a href="#">Absa Bank Kenya Plc</a><td>119,165<td>33.40<td class="hi">+0.30
<tr><td><a href="#">ALP</a><td>ALP Real Estate Investment Trust<td><td>1.02<td>
<tr><td><a href="#">SCOM</a><td>Safaricom Plc<td>1,290,262<td>36.45<td>-0.05
</table>
"""


def test_parser_reads_the_price_table():
    """The parser skips the 3-column table and reads every row of the price table."""
    # This parses the sample page.
    rows = parse_nse_table_rows(SAMPLE_HTML)
    # Three stocks were found.
    assert [row["ticker"] for row in rows] == ["ABSA", "ALP", "SCOM"]
    # Commas are removed from volume and prices are exact Decimals.
    assert rows[0]["volume"] == 119165 and rows[0]["price"] == Decimal("33.40")
    # An empty volume cell becomes None instead of breaking the row.
    assert rows[1]["volume"] is None and rows[1]["price"] == Decimal("1.02")
    # Only tracked tickers survive the filter (ABSA and SCOM, not ALP).
    assert [row["ticker"] for row in filter_tracked_stocks(rows)] == ["ABSA", "SCOM"]


def test_simulated_price_never_moves_more_than_the_limit():
    """1,000 simulated moves all stay within +/-1.5% and have 2 decimal places."""
    # This is the starting price.
    last_price = Decimal("100.00")
    # This runs the simulation many times.
    for _ in range(1000):
        # This gets one simulated price.
        new_price = simulate_next_price(last_price)
        # It stays within the limit (plus half a cent for rounding).
        assert abs(new_price - last_price) <= last_price * Decimal(str(FALLBACK_MAX_MOVE)) + Decimal("0.005")
        # It is rounded to cents.
        assert new_price == new_price.quantize(Decimal("0.01"))


def test_fallback_saves_a_price_for_every_tracked_stock(app):
    """With the site unreachable, every tracked stock still gets a price."""
    # Port 9 on this computer has nothing listening, so the request fails straight away.
    summary = run_full_scrape_once(source_url="http://127.0.0.1:9/")
    # The run reports that it used the fallback for all 15 stocks.
    assert summary["source"] == "fallback" and summary["price_rows_saved"] == len(TRACKED_TICKERS)
    # Stocks missing from the test database were created.
    assert Stock.query.count() >= len(TRACKED_TICKERS)
    # SCOM's simulated price starts from its last saved price, 36.55, and moves at most 1.5%.
    scom = Stock.query.filter_by(ticker="SCOM").one()
    newest = Price.query.filter_by(stock_id=scom.id).order_by(Price.recorded_at.desc()).first().close_price
    assert abs(newest - Decimal("36.55")) <= Decimal("36.55") * Decimal("0.015") + Decimal("0.005")
