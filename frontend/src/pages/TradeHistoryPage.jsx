// This imports React hooks: useEffect to load on open, useMemo to filter efficiently, useState to store data.
import { useEffect, useMemo, useState } from "react";
// This imports the icons used on the page.
import { Loader2, Search } from "lucide-react";
// This imports toast for error pop-ups.
import toast from "react-hot-toast";
// This imports the BUY/SELL badge.
import TradeTypeBadge from "../components/TradeTypeBadge";
// This imports the API client and error helper.
import api, { getErrorMessage } from "../services/api";
// This imports the formatting helpers.
import { changeColor, formatEAT, formatKES, formatSignedKES } from "../utils/format";

// These are the filter buttons.
const TYPE_FILTERS = [
  // Every trade.
  { value: "ALL", label: "All" },
  // Purchases only.
  { value: "BUY", label: "Buys" },
  // Sales only.
  { value: "SELL", label: "Sells" },
];

// This is the most trades the API returns in one request.
const HISTORY_LIMIT = 500;

// This page lists every trade the student has made, newest first.
export default function TradeHistoryPage() {
  // This holds every trade from /api/trades.
  const [trades, setTrades] = useState([]);
  // This is true while loading.
  const [isLoading, setIsLoading] = useState(true);
  // This is the selected BUY/SELL filter.
  const [typeFilter, setTypeFilter] = useState("ALL");
  // This is the text typed in the search box.
  const [search, setSearch] = useState("");

  // This loads the trades once when the page opens.
  useEffect(() => {
    // This asks for up to 500 trades.
    api
      .get("/trades", { params: { limit: HISTORY_LIMIT } })
      // This stores them.
      .then(({ data }) => setTrades(data))
      // A 401 is already handled by the API client.
      .catch((error) => error.response?.status !== 401 && toast.error(getErrorMessage(error)))
      // This hides the spinner.
      .finally(() => setIsLoading(false));
  }, []);

  // useMemo only re-filters when the trades or filters change, not on every redraw.
  const visibleTrades = useMemo(() => {
    // This normalises the search text, e.g. " scom" -> "SCOM".
    const query = search.trim().toUpperCase();
    // This keeps trades that match both the type filter and the search.
    return trades.filter(
      (trade) =>
        // This applies the BUY/SELL filter.
        (typeFilter === "ALL" || trade.trade_type === typeFilter) &&
        // This matches the ticker or company name.
        (!query || trade.ticker.includes(query) || trade.company_name.toUpperCase().includes(query)),
    );
  }, [trades, typeFilter, search]);

  // This adds up the visible trades for the summary line.
  const totals = useMemo(
    () =>
      visibleTrades.reduce(
        (sum, trade) => ({
          // Money spent on buys.
          bought: sum.bought + (trade.trade_type === "BUY" ? Number(trade.total_value) : 0),
          // Money received from sells.
          sold: sum.sold + (trade.trade_type === "SELL" ? Number(trade.total_value) : 0),
          // Profit or loss locked in by sells.
          realized: sum.realized + Number(trade.realized_pnl ?? 0),
        }),
        { bought: 0, sold: 0, realized: 0 },
      ),
    [visibleTrades],
  );

  // This shows a spinner until the trades arrive.
  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center gap-3 text-slate-500">
        <Loader2 className="h-6 w-6 animate-spin" aria-hidden="true" />
        Loading your trades...
      </div>
    );
  }

  // This returns the page layout.
  return (
    // This stacks the sections.
    <div className="space-y-6">
      {/* This is the title. */}
      <div>
        <h1 className="text-2xl font-bold">Trade history</h1>
        <p className="mt-1 text-slate-500">Every buy and sell you have made, newest first. Times are in Nairobi time (EAT).</p>
      </div>

      {/* This row holds the filters and the search box. */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* These are the BUY/SELL filter buttons. */}
        <div className="flex gap-1 rounded-lg bg-slate-100 p-1" role="group" aria-label="Filter by trade type">
          {TYPE_FILTERS.map((filter) => (
            // The selected filter is highlighted in white.
            <button
              key={filter.value}
              type="button"
              onClick={() => setTypeFilter(filter.value)}
              aria-pressed={typeFilter === filter.value}
              className={`rounded-md px-4 py-1.5 text-sm font-medium ${typeFilter === filter.value ? "bg-white shadow-sm" : "text-slate-500 hover:text-slate-900"}`}
            >
              {filter.label}
            </button>
          ))}
        </div>
        {/* This is the search box. */}
        <label className="relative">
          {/* This is the magnifying glass inside the box. */}
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
          {/* The visible label is the placeholder; aria-label names it for screen readers. */}
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search stock, e.g. SCOM"
            aria-label="Search by stock"
            className="w-64 rounded-lg border border-slate-300 py-2 pl-9 pr-3 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
          />
        </label>
      </div>

      {/* This is the summary of the visible trades. */}
      <div className="grid gap-4 sm:grid-cols-4">
        {[
          // Number of trades shown.
          { label: "Trades shown", value: visibleTrades.length.toLocaleString("en-KE"), colour: "" },
          // Total spent buying.
          { label: "Total bought", value: formatKES(totals.bought), colour: "" },
          // Total received selling.
          { label: "Total sold", value: formatKES(totals.sold), colour: "" },
          // Realised profit or loss.
          { label: "Realised profit / loss", value: formatSignedKES(totals.realized), colour: changeColor(totals.realized) },
        ].map((item) => (
          <div key={item.label} className="rounded-xl border border-slate-200 bg-white p-4">
            <p className="text-xs text-slate-500">{item.label}</p>
            <p className={`mt-1 text-lg font-semibold tabular-nums ${item.colour}`}>{item.value}</p>
          </div>
        ))}
      </div>

      {/* This card is the trades table. */}
      <section className="rounded-xl border border-slate-200 bg-white">
        {visibleTrades.length === 0 ? (
          // This explains an empty table.
          <p className="px-5 py-10 text-center text-sm text-slate-500">
            {trades.length === 0 ? "You haven't made any trades yet. Your buys and sells will appear here." : "No trades match your filters."}
          </p>
        ) : (
          // This lets the table scroll sideways on phones.
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              {/* These are the column headings. */}
              <thead className="text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-medium">Date (EAT)</th>
                  <th className="px-5 py-3 font-medium">Type</th>
                  <th className="px-5 py-3 font-medium">Stock</th>
                  <th className="px-5 py-3 text-right font-medium">Shares</th>
                  <th className="px-5 py-3 text-right font-medium">Price</th>
                  <th className="px-5 py-3 text-right font-medium">Total</th>
                  <th className="px-5 py-3 text-right font-medium">Realised P/L</th>
                </tr>
              </thead>
              {/* These are the trades. */}
              <tbody className="divide-y divide-slate-100">
                {visibleTrades.map((trade) => (
                  <tr key={trade.id} className="hover:bg-slate-50">
                    <td className="whitespace-nowrap px-5 py-3 text-slate-600">{formatEAT(trade.traded_at)}</td>
                    <td className="px-5 py-3">
                      <TradeTypeBadge type={trade.trade_type} />
                    </td>
                    <td className="px-5 py-3">
                      <p className="font-semibold">{trade.ticker}</p>
                      <p className="text-xs text-slate-500">{trade.company_name}</p>
                    </td>
                    <td className="px-5 py-3 text-right tabular-nums">{trade.quantity.toLocaleString("en-KE")}</td>
                    <td className="px-5 py-3 text-right tabular-nums">{formatKES(trade.price_at_trade)}</td>
                    <td className="px-5 py-3 text-right font-medium tabular-nums">{formatKES(trade.total_value)}</td>
                    {/* Buys have no realised profit or loss, so they show a dash. */}
                    <td className={`px-5 py-3 text-right tabular-nums ${changeColor(trade.realized_pnl)}`}>
                      {trade.realized_pnl === null ? "—" : formatSignedKES(trade.realized_pnl)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      {/* This explains the 500-trade cap if it is reached. */}
      {trades.length === HISTORY_LIMIT && <p className="text-xs text-slate-500">Showing your {HISTORY_LIMIT} most recent trades.</p>}
    </div>
  );
}
