"""Tests for buying, selling, profit and loss, and portfolio totals."""
# This imports Decimal for exact money comparisons.
from decimal import Decimal

# This imports pytest for parametrised tests.
import pytest

# This imports the shared helpers.
from conftest import register_and_login, set_price


def buy(client, headers, ticker, quantity):
    """Send a buy order and return the response."""
    # This calls the buy endpoint.
    return client.post("/api/trades/buy", json={"ticker": ticker, "quantity": quantity}, headers=headers)


def sell(client, headers, ticker, quantity):
    """Send a sell order and return the response."""
    # This calls the sell endpoint.
    return client.post("/api/trades/sell", json={"ticker": ticker, "quantity": quantity}, headers=headers)


def test_buying_takes_cash_and_adds_shares(client):
    """Buying 100 SCOM at 36.55 costs exactly 3,655.00."""
    # This creates a student.
    headers = register_and_login(client)
    # This buys, using lower-case to check the ticker is normalised.
    response = buy(client, headers, "scom", 100)
    # 201 means the trade was created.
    assert response.status_code == 201
    # 100,000 - 100 x 36.55 = 96,345.00.
    assert response.get_json()["cash_balance"] == "96345.00"
    # The holding appears in the portfolio.
    position = client.get("/api/portfolio", headers=headers).get_json()["positions"][0]
    assert position["ticker"] == "SCOM" and position["shares_held"] == 100


def test_weighted_average_and_realised_profit(client):
    """Average cost blends both buys; a later sale locks in the right profit and loss."""
    # This creates a student.
    headers = register_and_login(client)
    # 40 shares at 92.50.
    buy(client, headers, "KCB", 40)
    # The price rises and 40 more are bought at 120.00.
    set_price("KCB", "120.00")
    buy(client, headers, "KCB", 40)
    # (40 x 92.50 + 40 x 120.00) / 80 = 106.25.
    position = client.get("/api/portfolio", headers=headers).get_json()["positions"][0]
    assert position["average_buy_price"] == "106.25"
    # Selling 50 at 130.00 locks in (130.00 - 106.25) x 50 = 1,187.50.
    set_price("KCB", "130.00")
    assert sell(client, headers, "KCB", 50).get_json()["trade"]["realized_pnl"] == "1187.50"
    # Selling the last 30 at 100.00 locks in (100.00 - 106.25) x 30 = -187.50.
    set_price("KCB", "100.00")
    assert sell(client, headers, "KCB", 30).get_json()["trade"]["realized_pnl"] == "-187.50"
    # Selling everything removes the holding.
    assert client.get("/api/portfolio", headers=headers).get_json()["positions"] == []


def test_cannot_overspend_or_oversell(client):
    """Students cannot spend money they do not have or sell shares they do not own."""
    # This creates a student.
    headers = register_and_login(client)
    # 200 BAT x 559.00 = 111,800, more than KES 100,000.
    response = buy(client, headers, "BAT", 200)
    assert response.status_code == 400 and "Insufficient funds" in response.get_json()["message"]
    # Selling SCOM without owning any.
    response = sell(client, headers, "SCOM", 1)
    assert response.status_code == 400 and "only hold 0" in response.get_json()["message"]
    # The failed trades changed nothing.
    assert client.get("/api/portfolio", headers=headers).get_json()["cash_balance"] == "100000.00"


@pytest.mark.parametrize("quantity", [0, -5, 2.5, "10", True, None, 1_000_001])
def test_invalid_quantities_are_rejected(client, quantity):
    """Only whole numbers from 1 to 1,000,000 are accepted."""
    # This creates a student.
    headers = register_and_login(client)
    # Each bad quantity is a 400.
    assert buy(client, headers, "SCOM", quantity).status_code == 400


def test_unknown_stock_and_missing_token(client):
    """Unknown tickers return 404 and trading without logging in returns 401."""
    # This creates a student.
    headers = register_and_login(client)
    # A ticker we do not track.
    assert buy(client, headers, "FAKE", 1).status_code == 404
    # No token at all.
    assert client.post("/api/trades/buy", json={"ticker": "SCOM", "quantity": 1}).status_code == 401


def test_portfolio_totals_always_add_up(client):
    """Realised + unrealised profit equals the total return, and cash + shares equals total value."""
    # This creates a student with a mix of trades and price moves.
    headers = register_and_login(client)
    buy(client, headers, "SCOM", 300)
    buy(client, headers, "KCB", 50)
    set_price("SCOM", "38.00")
    sell(client, headers, "SCOM", 100)
    set_price("KCB", "90.00")
    # This reads the summary.
    summary = client.get("/api/portfolio", headers=headers).get_json()
    # This converts the text values to Decimal.
    value = {key: Decimal(summary[key]) for key in ("cash_balance", "holdings_value", "total_value", "realized_pnl", "unrealized_pnl", "total_return")}
    # Cash + shares = total value.
    assert value["cash_balance"] + value["holdings_value"] == value["total_value"]
    # Realised + unrealised = total return.
    assert value["realized_pnl"] + value["unrealized_pnl"] == value["total_return"]
    # Realised: (38.00 - 36.55) x 100 = 145.00.
    assert value["realized_pnl"] == Decimal("145.00")


def test_trade_history_is_newest_first_and_private(client):
    """Students see only their own trades, newest first."""
    # Two students trade.
    alice = register_and_login(client, email="alice@example.com")
    bob = register_and_login(client, email="bob@example.com")
    buy(client, alice, "SCOM", 10)
    buy(client, alice, "KCB", 5)
    buy(client, bob, "BAT", 1)
    # Alice's history.
    history = client.get("/api/trades", headers=alice).get_json()
    # Only her two trades, newest first.
    assert [trade["ticker"] for trade in history] == ["KCB", "SCOM"]
