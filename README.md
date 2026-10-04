# NSE Paper Trader

A web app that lets Strathmore University students practise buying and selling shares on the Nairobi Securities Exchange (NSE) with KES 100,000 of virtual money. Built for a BBIT final-year research project measuring whether three weeks of simulated trading improves investment confidence and market literacy.

## Features

- Live prices for 15 NSE stocks, scraped from afx.kwayisi.org every 30 minutes during market hours, with a ±1.5% random-walk fallback if the source is down
- Register, log in, change password, and reset a forgotten password by email
- Buy and sell shares (market orders) with a review-and-confirm step
- Dashboard, portfolio with allocation chart, trade history, and watchlist
- Leaderboard (names shortened for privacy) and a Learn section with lessons and a quiz

## Tech stack

| Part | Technology |
|---|---|
| Backend | Python, Flask 3, SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt, APScheduler, BeautifulSoup4 |
| Database | PostgreSQL |
| Frontend | React 18, Vite, Tailwind CSS 4, React Router, Recharts, Axios |
| Tests | pytest |

## First-time setup (Windows, PowerShell)

1. Install Python 3.11+, Node.js 20.19+ or 22.12+, and PostgreSQL.
2. Create an empty database called `nse_paper_trader` in PostgreSQL.
3. Backend:
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
   Copy-Item .env.example .env   # then edit .env with your database password and a JWT secret
   .\.venv\Scripts\python.exe init_db.py
   ```
4. Frontend:
   ```powershell
   cd frontend
   npm install
   ```

## Running the app

Open two terminals in the project folder:

```powershell
# Terminal 1: backend API on http://127.0.0.1:5000
cd backend; .\.venv\Scripts\python.exe run.py

# Terminal 2: frontend on http://localhost:5173
npm --prefix frontend run dev
```

Then open http://localhost:5173. The backend scrapes prices once at startup (unless prices are under 30 minutes old) and then every 30 minutes, Monday to Friday, 09:00–15:30 East Africa Time.

Set `FLASK_DEBUG=1` in `backend/.env` for auto-reload during development. Keep it `0` when real participants use the app.

## Running the tests

```powershell
.\backend\.venv\Scripts\python.exe -m pytest
```

Tests use a separate database, `nse_paper_trader_test`, which they create automatically. Your real data is never touched.

## Useful scripts

```powershell
# Run one scrape now and save prices
$env:PYTHONPATH="backend"; .\backend\.venv\Scripts\python.exe scripts\run_scraper_once.py

# Check the price source is reachable and parsable
$env:PYTHONPATH="backend"; .\backend\.venv\Scripts\python.exe scripts\test_fetch_nse.py
```

## Project structure

```
backend/app/
  config/settings.py   settings read from backend/.env
  models/              database tables (SQLAlchemy)
  routes/              API endpoints: auth, stocks, trades, portfolio, watchlist, leaderboard
  services/            business rules: trading, password reset, email, leaderboard
  scraper/             NSE price scraper and scheduler
frontend/src/
  pages/               one file per page
  components/          shared building blocks
  context/             login state
  services/api.js      API client
  data/                Learn page content
tests/                 automated backend tests
```

## Disclaimer

For education only; not financial advice. Prices are scraped from public data and may be delayed.
