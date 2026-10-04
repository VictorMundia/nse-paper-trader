"""Tests for the stock list, price history, watchlist, and leaderboard."""
# This imports the shared helpers.
from conftest import register_and_login, set_price


def test_stock_list_detail_and_unknown_stock(client):
    """Stocks are public; the detail works in any capitals; unknown tickers are 404."""
    # The list shows all seeded stocks alphabetically.
    assert [stock["ticker"] for stock in client.get("/api/stocks").get_json()] == ["BAT", "KCB", "SCOM"]
    # Lower-case works.
    assert client.get("/api/stocks/scom").get_json()["price"] == "36.55"
    # Unknown ticker.
    assert client.get("/api/stocks/XYZ").status_code == 404


def test_change_is_measured_from_the_previous_price(client):
    """A new price shows its change from the one before."""
    # SCOM moves from 36.55 to 37.00.
    set_price("SCOM", "37.00")
    # This reads the stock.
    stock = client.get("/api/stocks/SCOM").get_json()
    # 37.00 - 36.55 = 0.45.
    assert stock["change"] == "0.45" and stock["previous_price"] == "36.55"


def test_price_history_validates_days(client):
    """?days must be a whole number from 1 to 365; bad values are 400, not silently ignored."""
    # A valid request.
    assert client.get("/api/stocks/SCOM/prices?days=7").status_code == 200
    # Each bad value is rejected.
    for bad in ("abc", "0", "999", "2.5"):
        assert client.get(f"/api/stocks/SCOM/prices?days={bad}").status_code == 400


def test_watchlist_add_list_and_remove(client):
    """Starring is idempotent, case-insensitive, and private to each student."""
    # This creates a student.
    headers = register_and_login(client)
    # A new list is empty.
    assert client.get("/api/watchlist", headers=headers).get_json() == []
    # Adding creates (201); adding again is fine (200).
    assert client.post("/api/watchlist", json={"ticker": "scom"}, headers=headers).status_code == 201
    assert client.post("/api/watchlist", json={"ticker": "SCOM"}, headers=headers).status_code == 200
    # Unknown stock.
    assert client.post("/api/watchlist", json={"ticker": "FAKE"}, headers=headers).status_code == 404
    # The list has SCOM once.
    assert [stock["ticker"] for stock in client.get("/api/watchlist", headers=headers).get_json()] == ["SCOM"]
    # Removing works, and removing again is fine.
    assert client.delete("/api/watchlist/scom", headers=headers).status_code == 200
    assert client.delete("/api/watchlist/SCOM", headers=headers).status_code == 200
    # The list is empty again.
    assert client.get("/api/watchlist", headers=headers).get_json() == []


def test_leaderboard_ranks_ties_filters_and_privacy(client):
    """Equal values share a rank, non-traders are left out, levels filter, and no private data leaks."""
    # Three traders and one non-trader.
    alice = register_and_login(client, email="a@example.com", full_name="Alice Wanjiru", level="beginner")
    esther = register_and_login(client, email="e@example.com", full_name="Esther Njeri", level="beginner")
    brian = register_and_login(client, email="b@example.com", full_name="Brian Otieno", level="advanced")
    register_and_login(client, email="d@example.com", full_name="David Mutua", level="beginner")
    # Alice and Esther buy the same; Brian buys KCB.
    client.post("/api/trades/buy", json={"ticker": "SCOM", "quantity": 100}, headers=alice)
    client.post("/api/trades/buy", json={"ticker": "SCOM", "quantity": 100}, headers=esther)
    client.post("/api/trades/buy", json={"ticker": "KCB", "quantity": 100}, headers=brian)
    # SCOM rises and KCB falls.
    set_price("SCOM", "38.00")
    set_price("KCB", "90.00")
    # This reads the leaderboard as Alice.
    board = client.get("/api/leaderboard", headers=alice).get_json()
    # This pairs names with ranks.
    ranking = [(entry["display_name"], entry["rank"]) for entry in board["entries"]]
    # Alice and Esther tie at #1, so Brian is #3; David never traded and is not listed.
    assert sorted(ranking[:2]) == [("Alice W.", 1), ("Esther N.", 1)] and ranking[2] == ("Brian O.", 3)
    # Alice's own rank is reported.
    assert board["you"]["rank"] == 1 and board["ranked_count"] == 3
    # No emails, full names, or IDs are sent.
    assert not any(key in entry for entry in board["entries"] for key in ("email", "full_name", "user_id", "id"))
    # The beginners filter leaves out Brian.
    beginners = client.get("/api/leaderboard?level=beginner", headers=alice).get_json()
    assert {entry["display_name"] for entry in beginners["entries"]} == {"Alice W.", "Esther N."}
    # An unknown level and a missing token are rejected.
    assert client.get("/api/leaderboard?level=expert", headers=alice).status_code == 400
    assert client.get("/api/leaderboard").status_code == 401
