// This imports React hooks: useCallback for a stable load function, useEffect to load on open, useState to store data.
import { useCallback, useEffect, useState } from "react";
// This imports router tools: Link for the back link, useParams to read the ticker from the URL.
import { Link, useParams } from "react-router-dom";
// This imports the icons used on the page.
import { ArrowLeft, Loader2 } from "lucide-react";
// This imports toast for error pop-ups.
import toast from "react-hot-toast";
// This imports the page's building blocks.
import PriceChart from "../components/PriceChart";
import TradePanel from "../components/TradePanel";
import WatchlistStar from "../components/WatchlistStar";
// This imports the profile refresh, so the navbar balance updates after a trade.
import { useAuth } from "../context/AuthContext";
// This imports the API client and error helper.
import api, { getErrorMessage } from "../services/api";
// This imports the formatting helpers.
import { changeColor, formatEAT, formatKES, formatPercent, formatSignedKES } from "../utils/format";

// This page shows one stock: price, chart, the student's position, and the trade panel.
export default function StockDetailPage() {
  // This reads the ticker from the URL, e.g. /stocks/SCOM -> "SCOM".
  const { ticker } = useParams();
  // This reads the function that reloads the navbar balance.
  const { refreshUser } = useAuth();
  // This holds the stock from /api/stocks/<ticker>.
  const [stock, setStock] = useState(null);
  // This holds the portfolio, for cash and the student's holding of this stock.
  const [portfolio, setPortfolio] = useState(null);
  // This is true when the stock is on the watchlist.
  const [isWatched, setIsWatched] = useState(false);
  // This is true if the ticker does not exist.
  const [notFound, setNotFound] = useState(false);

  // This loads everything the page needs in parallel.
  const loadPage = useCallback(async () => {
    // This guards the requests.
    try {
      // Four requests run at the same time.
      const [stockRes, portfolioRes, watchlistRes] = await Promise.all([
        // The stock and its latest price.
        api.get(`/stocks/${ticker}`),
        // Cash and holdings.
        api.get("/portfolio"),
        // The starred stocks.
        api.get("/watchlist"),
        // This also refreshes the navbar balance.
        refreshUser(),
      ]);
      // This stores the stock.
      setStock(stockRes.data);
      // This stores the portfolio.
      setPortfolio(portfolioRes.data);
      // This checks whether this stock is starred.
      setIsWatched(watchlistRes.data.some((item) => item.ticker === stockRes.data.ticker));
    } catch (error) {
      // An unknown ticker shows the "not found" message.
      if (error.response?.status === 404) setNotFound(true);
      // Other errors (except 401, already handled) show a pop-up.
      else if (error.response?.status !== 401) toast.error(getErrorMessage(error));
    }
  }, [ticker, refreshUser]);

  // This loads when the page opens or the ticker in the URL changes.
  useEffect(() => {
    // This starts the load.
    loadPage();
  }, [loadPage]);

  // This is shown for an unknown ticker such as /stocks/XYZ.
  if (notFound) {
    return (
      <div className="space-y-4 py-10 text-center">
        <p className="text-lg font-semibold">Stock &quot;{ticker}&quot; was not found.</p>
        <Link to="/stocks" className="text-emerald-700 hover:underline">
          Back to all stocks
        </Link>
      </div>
    );
  }

  // This shows a spinner until the data arrives.
  if (!stock || !portfolio) {
    return (
      <div className="flex h-64 items-center justify-center gap-3 text-slate-500">
        <Loader2 className="h-6 w-6 animate-spin" aria-hidden="true" />
        Loading {ticker.toUpperCase()}...
      </div>
    );
  }

  // This finds the student's holding of this stock, if any.
  const position = portfolio.positions.find((item) => item.ticker === stock.ticker);

  // This returns the page layout.
  return (
    // This stacks the sections.
    <div className="space-y-6">
      {/* This is the link back to the list. */}
      <Link to="/stocks" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900">
        <ArrowLeft className="h-4 w-4" aria-hidden="true" />
        All stocks
      </Link>

      {/* This is the header: name, star, price, and change. */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          {/* This is the ticker with the watchlist star. */}
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold">{stock.ticker}</h1>
            <WatchlistStar ticker={stock.ticker} isWatched={isWatched} onToggle={(_, value) => setIsWatched(value)} size="h-6 w-6" />
          </div>
          {/* This is the company name. */}
          <p className="text-slate-500">{stock.company_name}</p>
        </div>
        {/* This is the latest price and the change since the previous update. */}
        <div className="text-right">
          <p className="text-3xl font-semibold tabular-nums">{formatKES(stock.price)}</p>
          <p className={`text-sm font-medium tabular-nums ${changeColor(stock.change)}`}>
            {formatSignedKES(stock.change)} ({formatPercent(stock.change_percent)}) since last update
          </p>
          <p className="text-xs text-slate-400">Updated {formatEAT(stock.last_updated)} EAT</p>
        </div>
      </div>

      {/* This is the chart and the trade panel: side by side on large screens. */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* The chart takes 2 of 3 columns. */}
        <div className="lg:col-span-2">
          <PriceChart ticker={stock.ticker} companyName={stock.company_name} />
        </div>
        {/* The trade panel and position take 1 column. */}
        <div className="space-y-6">
          {/* key resets the panel's form when the student opens a different stock. */}
          <TradePanel key={stock.ticker} stock={stock} cash={portfolio.cash_balance} sharesHeld={position?.shares_held ?? 0} onTraded={loadPage} />

          {/* This card shows the student's holding of this stock. */}
          <section className="rounded-xl border border-slate-200 bg-white p-5 text-sm">
            <h2 className="font-semibold">Your position</h2>
            {position ? (
              // This lists the holding's details.
              <dl className="mt-3 space-y-1.5">
                <div className="flex justify-between"><dt className="text-slate-500">Shares held</dt><dd className="font-medium tabular-nums">{position.shares_held.toLocaleString("en-KE")}</dd></div>
                <div className="flex justify-between"><dt className="text-slate-500">Average buy price</dt><dd className="font-medium tabular-nums">{formatKES(position.average_buy_price)}</dd></div>
                <div className="flex justify-between"><dt className="text-slate-500">Current value</dt><dd className="font-medium tabular-nums">{formatKES(position.market_value)}</dd></div>
                <div className="flex justify-between border-t border-slate-100 pt-1.5">
                  <dt className="text-slate-500">Unrealised profit / loss</dt>
                  <dd className={`font-semibold tabular-nums ${changeColor(position.unrealized_pnl)}`}>
                    {formatSignedKES(position.unrealized_pnl)} ({formatPercent(position.unrealized_pnl_percent)})
                  </dd>
                </div>
              </dl>
            ) : (
              // This is shown before the first purchase.
              <p className="mt-2 text-slate-500">You don&apos;t own any {stock.ticker} shares yet.</p>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
