// This imports React hooks: useEffect to load on open, useMemo to filter efficiently, useState to store data.
import { useEffect, useMemo, useState } from "react";
// This imports Link so each card opens its stock's page.
import { Link } from "react-router-dom";
// This imports the icons used on the page.
import { Loader2, Search } from "lucide-react";
// This imports toast for error pop-ups.
import toast from "react-hot-toast";
// This imports the watchlist star.
import WatchlistStar from "../components/WatchlistStar";
// This imports the API client and error helper.
import api, { getErrorMessage } from "../services/api";
// This imports the formatting helpers.
import { changeColor, formatEAT, formatKES, formatPercent } from "../utils/format";

// This page lists all tracked NSE stocks as cards.
export default function StocksPage() {
  // This holds the 15 stocks.
  const [stocks, setStocks] = useState([]);
  // This holds the tickers on the student's watchlist; a Set makes "is it starred?" a quick check.
  const [watched, setWatched] = useState(new Set());
  // This is true while loading.
  const [isLoading, setIsLoading] = useState(true);
  // This is the text typed in the search box.
  const [search, setSearch] = useState("");
  // This is true when only watchlist stocks are shown.
  const [watchlistOnly, setWatchlistOnly] = useState(false);

  // This loads stocks and the watchlist in parallel once when the page opens.
  useEffect(() => {
    // Both requests run at the same time.
    Promise.all([api.get("/stocks"), api.get("/watchlist")])
      // This stores the results.
      .then(([stocksRes, watchlistRes]) => {
        // This stores the stocks.
        setStocks(stocksRes.data);
        // This stores the starred tickers.
        setWatched(new Set(watchlistRes.data.map((stock) => stock.ticker)));
      })
      // A 401 is already handled by the API client.
      .catch((error) => error.response?.status !== 401 && toast.error(getErrorMessage(error)))
      // This hides the spinner.
      .finally(() => setIsLoading(false));
  }, []);

  // This updates the starred set after a star is clicked.
  const handleToggle = (ticker, isNowWatched) =>
    setWatched((current) => {
      // A new Set is made because React only redraws when the state object changes.
      const next = new Set(current);
      // This adds or removes the ticker.
      if (isNowWatched) next.add(ticker);
      else next.delete(ticker);
      // This stores the new set.
      return next;
    });

  // This applies the search and the watchlist filter.
  const visibleStocks = useMemo(() => {
    // This normalises the search, e.g. " kcb" -> "KCB".
    const query = search.trim().toUpperCase();
    // This keeps stocks that pass both filters.
    return stocks.filter(
      (stock) =>
        // This applies the watchlist filter.
        (!watchlistOnly || watched.has(stock.ticker)) &&
        // This matches the ticker or company name.
        (!query || stock.ticker.includes(query) || stock.company_name.toUpperCase().includes(query)),
    );
  }, [stocks, watched, search, watchlistOnly]);

  // This shows a spinner until the data arrives.
  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center gap-3 text-slate-500">
        <Loader2 className="h-6 w-6 animate-spin" aria-hidden="true" />
        Loading stocks...
      </div>
    );
  }

  // This finds the newest update time to show under the title.
  const lastUpdated = stocks.reduce((latest, stock) => (stock.last_updated > latest ? stock.last_updated : latest), "");

  // This returns the page layout.
  return (
    // This stacks the sections.
    <div className="space-y-6">
      {/* This is the title. */}
      <div>
        <h1 className="text-2xl font-bold">Stocks</h1>
        <p className="mt-1 text-slate-500">
          {stocks.length} Nairobi Securities Exchange stocks · prices updated {formatEAT(lastUpdated)} EAT. Click a stock to see its chart and trade.
        </p>
      </div>

      {/* This row holds the filter and the search box. */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* These are the All / Watchlist filter buttons. */}
        <div className="flex gap-1 rounded-lg bg-slate-100 p-1" role="group" aria-label="Filter stocks">
          {[
            // Every stock.
            { value: false, label: "All stocks" },
            // Starred stocks only, with a count.
            { value: true, label: `Watchlist (${watched.size})` },
          ].map((option) => (
            <button
              key={option.label}
              type="button"
              onClick={() => setWatchlistOnly(option.value)}
              aria-pressed={watchlistOnly === option.value}
              className={`rounded-md px-4 py-1.5 text-sm font-medium ${watchlistOnly === option.value ? "bg-white shadow-sm" : "text-slate-500 hover:text-slate-900"}`}
            >
              {option.label}
            </button>
          ))}
        </div>
        {/* This is the search box. */}
        <label className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search, e.g. Safaricom"
            aria-label="Search stocks"
            className="w-64 rounded-lg border border-slate-300 py-2 pl-9 pr-3 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
          />
        </label>
      </div>

      {visibleStocks.length === 0 ? (
        // This explains an empty result.
        <p className="rounded-xl border border-dashed border-slate-300 bg-white px-5 py-10 text-center text-sm text-slate-500">
          {watchlistOnly && watched.size === 0 ? "Your watchlist is empty. Tap the ☆ on any stock to follow it." : "No stocks match your search."}
        </p>
      ) : (
        // This is the grid of stock cards: 1 column on phones up to 3 on laptops.
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {visibleStocks.map((stock) => (
            // relative lets the star sit on top of the card's link.
            <div key={stock.ticker} className="relative">
              {/* The whole card links to the stock's page. */}
              <Link to={`/stocks/${stock.ticker}`} className="block rounded-xl border border-slate-200 bg-white p-5 transition hover:border-emerald-300 hover:shadow-sm">
                {/* This is the ticker and company; pr-8 leaves room for the star. */}
                <p className="pr-8 text-lg font-bold">{stock.ticker}</p>
                <p className="truncate pr-8 text-sm text-slate-500">{stock.company_name}</p>
                {/* This is the price and change. */}
                <div className="mt-4 flex items-end justify-between">
                  <p className="text-xl font-semibold tabular-nums">{formatKES(stock.price)}</p>
                  <p className={`text-sm font-medium tabular-nums ${changeColor(stock.change)}`}>{formatPercent(stock.change_percent)}</p>
                </div>
              </Link>
              {/* The star sits in the top-right corner, outside the link so clicking it does not open the page. */}
              <div className="absolute right-3 top-3">
                <WatchlistStar ticker={stock.ticker} isWatched={watched.has(stock.ticker)} onToggle={handleToggle} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
