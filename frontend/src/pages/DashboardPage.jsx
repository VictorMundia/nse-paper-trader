// This imports React hooks: useCallback for a stable load function, useEffect to load on open, useState to store data.
import { useCallback, useEffect, useState } from "react";
// This imports Link to jump to other pages.
import { Link } from "react-router-dom";
// This imports the icons used on the page.
import { Briefcase, Loader2, PiggyBank, RefreshCw, TrendingUp, Wallet } from "lucide-react";
// This imports toast for error pop-ups.
import toast from "react-hot-toast";
// This imports the dashboard building blocks.
import MarketTable from "../components/MarketTable";
import PriceChart from "../components/PriceChart";
import StatCard from "../components/StatCard";
// This imports the logged-in student's profile and the refresh action for the navbar balance.
import { useAuth } from "../context/AuthContext";
// This imports the shared API client and error helper.
import api, { getErrorMessage } from "../services/api";
// This imports the formatting helpers.
import { changeColor, formatEAT, formatKES, formatPercent, formatSignedKES } from "../utils/format";

// This is the home page after login: account summary, live market, holdings, and recent trades.
export default function DashboardPage() {
  // This reads the student's profile and the function that reloads it.
  const { user, refreshUser } = useAuth();
  // This holds the portfolio summary from /api/portfolio.
  const [portfolio, setPortfolio] = useState(null);
  // This holds the 15 stocks from /api/stocks.
  const [stocks, setStocks] = useState([]);
  // This holds the 5 most recent trades from /api/trades.
  const [trades, setTrades] = useState([]);
  // This is the stock shown in the chart.
  const [selectedStock, setSelectedStock] = useState(null);
  // This is true while any data is loading.
  const [isLoading, setIsLoading] = useState(true);

  // This loads everything the dashboard needs in parallel.
  const loadDashboard = useCallback(async () => {
    // This shows the loading state.
    setIsLoading(true);
    // This guards the requests.
    try {
      // Promise.all sends the four requests at the same time instead of one after another.
      const [portfolioRes, stocksRes, tradesRes] = await Promise.all([
        // Holdings, cash, and total value.
        api.get("/portfolio"),
        // The 15 stocks with latest prices.
        api.get("/stocks"),
        // The five latest trades.
        api.get("/trades", { params: { limit: 5 } }),
        // This also refreshes the navbar cash balance.
        refreshUser(),
      ]);
      // This stores the portfolio.
      setPortfolio(portfolioRes.data);
      // This stores the stocks.
      setStocks(stocksRes.data);
      // This stores the trades.
      setTrades(tradesRes.data);
      // This picks the first stock for the chart, keeping the current choice on refresh; Safaricom is the most traded.
      setSelectedStock((current) => current ?? stocksRes.data.find((stock) => stock.ticker === "SCOM") ?? stocksRes.data[0] ?? null);
    } catch (error) {
      // This shows what went wrong; a 401 is already handled by the API client.
      if (error.response?.status !== 401) toast.error(getErrorMessage(error));
    } finally {
      // This hides the loading state.
      setIsLoading(false);
    }
  }, [refreshUser]);

  // This loads the dashboard once when the page opens.
  useEffect(() => {
    // This starts the load.
    loadDashboard();
  }, [loadDashboard]);

  // This shows a spinner until the first load finishes.
  if (!portfolio) {
    return (
      <div className="flex h-64 items-center justify-center gap-3 text-slate-500">
        <Loader2 className="h-6 w-6 animate-spin" aria-hidden="true" />
        Loading your dashboard...
      </div>
    );
  }

  // This returns the page layout.
  return (
    // This stacks the sections with space between them.
    <div className="space-y-6">
      {/* This is the greeting row with the refresh button. */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        {/* This is the greeting. */}
        <div>
          {/* This greets the student by first name. */}
          <h1 className="text-2xl font-bold">Hello, {user.full_name.split(" ")[0]}</h1>
          {/* This reminds them the money is virtual and shows their level. */}
          <p className="mt-1 text-slate-500">
            Your virtual trading account · <span className="capitalize">{user.experience_level}</span> investor
          </p>
        </div>
        {/* This button reloads all dashboard data. */}
        <button
          type="button"
          onClick={loadDashboard}
          disabled={isLoading}
          className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 disabled:opacity-60"
        >
          {/* The icon spins while loading. */}
          <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} aria-hidden="true" />
          Refresh
        </button>
      </div>

      {/* These are the four summary cards: 1 column on phones, 2 on tablets, 4 on laptops. */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total account value = cash + shares. */}
        <StatCard icon={PiggyBank} label="Total account value" value={formatKES(portfolio.total_value)} detail={`Started with ${formatKES(portfolio.starting_balance)}`} />
        {/* Overall gain or loss since registering. */}
        <StatCard
          icon={TrendingUp}
          label="Total return"
          value={formatSignedKES(portfolio.total_return)}
          detail={`${formatPercent(portfolio.total_return_percent)} since you started`}
          detailClass={changeColor(portfolio.total_return)}
          accent={changeColor(portfolio.total_return)}
        />
        {/* Cash the student can still spend. */}
        <StatCard icon={Wallet} label="Cash available" value={formatKES(portfolio.cash_balance)} accent="text-sky-600" />
        {/* Current value of all shares owned. */}
        <StatCard
          icon={Briefcase}
          label="Shares value"
          value={formatKES(portfolio.holdings_value)}
          detail={`${portfolio.positions.length} ${portfolio.positions.length === 1 ? "stock" : "stocks"} held`}
          accent="text-amber-600"
        />
      </div>

      {/* This is the chart and market table: side by side on large screens. */}
      <div className="grid gap-6 lg:grid-cols-5">
        {/* The chart takes 3 of 5 columns. */}
        <div className="lg:col-span-3">
          {selectedStock && <PriceChart ticker={selectedStock.ticker} companyName={selectedStock.company_name} />}
          {/* This hint explains the table is clickable. */}
          <p className="mt-2 text-xs text-slate-500">Tip: click any stock in the market table to see its chart.</p>
        </div>
        {/* The table takes 2 of 5 columns and scrolls if long. */}
        <div className="lg:col-span-2 lg:max-h-[26rem] lg:overflow-y-auto">
          <MarketTable stocks={stocks} selectedTicker={selectedStock?.ticker} onSelect={setSelectedStock} />
        </div>
      </div>

      {/* These are the holdings and recent trades: side by side on large screens. */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* This card lists the stocks the student owns. */}
        <section className="rounded-xl border border-slate-200 bg-white">
          {/* This is the card header. */}
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
            <h2 className="font-semibold">Your holdings</h2>
            <Link to="/portfolio" className="text-sm text-emerald-700 hover:underline">
              View portfolio
            </Link>
          </div>
          {portfolio.positions.length === 0 ? (
            // This is shown before the first purchase.
            <p className="px-5 py-8 text-center text-sm text-slate-500">
              You don&apos;t own any shares yet. Your KES 100,000 is ready to invest.
            </p>
          ) : (
            // This lists each holding.
            <ul className="divide-y divide-slate-100">
              {portfolio.positions.map((position) => (
                <li key={position.ticker} className="flex items-center justify-between px-5 py-3 text-sm">
                  {/* This is the ticker and share count. */}
                  <div>
                    <p className="font-semibold">{position.ticker}</p>
                    <p className="text-xs text-slate-500">
                      {position.shares_held} shares @ avg {formatKES(position.average_buy_price)}
                    </p>
                  </div>
                  {/* This is the current value and the paper profit or loss. */}
                  <div className="text-right">
                    <p className="font-medium tabular-nums">{formatKES(position.market_value)}</p>
                    <p className={`text-xs tabular-nums ${changeColor(position.unrealized_pnl)}`}>
                      {formatSignedKES(position.unrealized_pnl)} ({formatPercent(position.unrealized_pnl_percent)})
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* This card lists the five most recent trades. */}
        <section className="rounded-xl border border-slate-200 bg-white">
          {/* This is the card header. */}
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
            <h2 className="font-semibold">Recent trades</h2>
            <Link to="/history" className="text-sm text-emerald-700 hover:underline">
              View all
            </Link>
          </div>
          {trades.length === 0 ? (
            // This is shown before the first trade.
            <p className="px-5 py-8 text-center text-sm text-slate-500">No trades yet. Your buys and sells will appear here.</p>
          ) : (
            // This lists each trade.
            <ul className="divide-y divide-slate-100">
              {trades.map((trade) => (
                <li key={trade.id} className="flex items-center justify-between px-5 py-3 text-sm">
                  {/* This is the BUY/SELL badge, ticker, and time. */}
                  <div className="flex items-center gap-3">
                    <span className={`rounded px-2 py-0.5 text-xs font-semibold ${trade.trade_type === "BUY" ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`}>
                      {trade.trade_type}
                    </span>
                    <div>
                      <p className="font-semibold">
                        {trade.quantity} {trade.ticker}
                      </p>
                      <p className="text-xs text-slate-500">{formatEAT(trade.traded_at)} EAT</p>
                    </div>
                  </div>
                  {/* This is the total value and, for sells, the realised profit or loss. */}
                  <div className="text-right">
                    <p className="font-medium tabular-nums">{formatKES(trade.total_value)}</p>
                    {trade.realized_pnl !== null && (
                      <p className={`text-xs tabular-nums ${changeColor(trade.realized_pnl)}`}>{formatSignedKES(trade.realized_pnl)} realised</p>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
