// This imports React hooks: useCallback for a stable load function, useEffect to load on open, useState to store data.
import { useCallback, useEffect, useState } from "react";
// This imports the Recharts pieces for the allocation doughnut chart.
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
// This imports the icons used on the page.
import { Briefcase, CircleDollarSign, Info, Loader2, PiggyBank, RefreshCw, Wallet } from "lucide-react";
// This imports toast for error pop-ups.
import toast from "react-hot-toast";
// This imports the summary card.
import StatCard from "../components/StatCard";
// This imports the profile refresh, so the navbar balance stays in sync.
import { useAuth } from "../context/AuthContext";
// This imports the API client and error helper.
import api, { getErrorMessage } from "../services/api";
// This imports the formatting helpers.
import { changeColor, formatKES, formatPercent, formatSignedKES } from "../utils/format";

// These are the slice colours; cash is always grey so it stands apart from stocks.
const SLICE_COLOURS = ["#059669", "#0284c7", "#d97706", "#7c3aed", "#db2777", "#0d9488", "#65a30d", "#dc2626", "#4f46e5", "#ca8a04"];
// This is the colour for the cash slice.
const CASH_COLOUR = "#94a3b8";

// This page shows every holding, how the money is split, and where profit or loss came from.
export default function PortfolioPage() {
  // This reads the function that reloads the navbar balance.
  const { refreshUser } = useAuth();
  // This holds the summary from /api/portfolio.
  const [portfolio, setPortfolio] = useState(null);
  // This is true while loading.
  const [isLoading, setIsLoading] = useState(true);

  // This loads the portfolio and refreshes the navbar balance at the same time.
  const loadPortfolio = useCallback(async () => {
    // This shows the loading state.
    setIsLoading(true);
    // This guards the requests.
    try {
      // Both requests run in parallel.
      const [{ data }] = await Promise.all([api.get("/portfolio"), refreshUser()]);
      // This stores the summary.
      setPortfolio(data);
    } catch (error) {
      // A 401 is already handled by the API client.
      if (error.response?.status !== 401) toast.error(getErrorMessage(error));
    } finally {
      // This hides the loading state.
      setIsLoading(false);
    }
  }, [refreshUser]);

  // This loads once when the page opens.
  useEffect(() => {
    // This starts the load.
    loadPortfolio();
  }, [loadPortfolio]);

  // This shows a spinner until the first load finishes.
  if (!portfolio) {
    return (
      <div className="flex h-64 items-center justify-center gap-3 text-slate-500">
        <Loader2 className="h-6 w-6 animate-spin" aria-hidden="true" />
        Loading your portfolio...
      </div>
    );
  }

  // This is the total account value as a number, used for percentages.
  const totalValue = Number(portfolio.total_value);
  // This sorts holdings from largest to smallest value.
  const positions = [...portfolio.positions].sort((a, b) => Number(b.market_value) - Number(a.market_value));
  // This builds the chart slices: one per stock plus cash.
  const slices = [
    // One slice per holding, coloured from the palette.
    ...positions.map((position, index) => ({ name: position.ticker, value: Number(position.market_value), colour: SLICE_COLOURS[index % SLICE_COLOURS.length] })),
    // The cash slice.
    { name: "Cash", value: Number(portfolio.cash_balance), colour: CASH_COLOUR },
    // Empty slices are dropped so they do not appear in the legend.
  ].filter((slice) => slice.value > 0);

  // This returns the page layout.
  return (
    // This stacks the sections.
    <div className="space-y-6">
      {/* This is the title row with the refresh button. */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        {/* This is the title. */}
        <div>
          <h1 className="text-2xl font-bold">Portfolio</h1>
          <p className="mt-1 text-slate-500">Your holdings valued at the latest NSE prices.</p>
        </div>
        {/* This reloads the page data. */}
        <button
          type="button"
          onClick={loadPortfolio}
          disabled={isLoading}
          className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 disabled:opacity-60"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} aria-hidden="true" />
          Refresh
        </button>
      </div>

      {/* These are the four summary cards. */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total value, with the overall return underneath. */}
        <StatCard
          icon={PiggyBank}
          label="Total account value"
          value={formatKES(portfolio.total_value)}
          detail={`${formatSignedKES(portfolio.total_return)} (${formatPercent(portfolio.total_return_percent)}) overall`}
          detailClass={changeColor(portfolio.total_return)}
        />
        {/* Cash still available to invest. */}
        <StatCard icon={Wallet} label="Cash available" value={formatKES(portfolio.cash_balance)} accent="text-sky-600" />
        {/* Paper profit or loss on shares still held. */}
        <StatCard
          icon={Briefcase}
          label="Unrealised profit / loss"
          value={formatSignedKES(portfolio.unrealized_pnl)}
          detail="On shares you still hold"
          accent={changeColor(portfolio.unrealized_pnl)}
        />
        {/* Profit or loss already locked in by selling. */}
        <StatCard
          icon={CircleDollarSign}
          label="Realised profit / loss"
          value={formatSignedKES(portfolio.realized_pnl)}
          detail="Locked in by selling"
          accent={changeColor(portfolio.realized_pnl)}
        />
      </div>

      {/* This is the chart and explanation: side by side on large screens. */}
      <div className="grid gap-6 lg:grid-cols-5">
        {/* This card holds the allocation doughnut chart. */}
        <section className="rounded-xl border border-slate-200 bg-white p-5 lg:col-span-3">
          <h2 className="font-semibold">Where your money is</h2>
          <p className="text-sm text-slate-500">Share of your {formatKES(portfolio.total_value)} account in each stock and in cash.</p>
          {/* This is the chart and its legend side by side. */}
          <div className="mt-4 grid items-center gap-4 sm:grid-cols-2">
            {/* The chart needs a fixed height to draw into. */}
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  {/* innerRadius makes it a doughnut; each slice gets its colour. */}
                  <Pie data={slices} dataKey="value" nameKey="name" innerRadius="55%" outerRadius="90%" paddingAngle={1} stroke="none">
                    {slices.map((slice) => (
                      <Cell key={slice.name} fill={slice.colour} />
                    ))}
                  </Pie>
                  {/* This shows the value on hover. */}
                  <Tooltip formatter={(value, name) => [formatKES(value), name]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            {/* This is the legend with percentages. */}
            <ul className="space-y-2 text-sm">
              {slices.map((slice) => (
                <li key={slice.name} className="flex items-center justify-between gap-3">
                  {/* This is the colour dot and name. */}
                  <span className="flex items-center gap-2">
                    <span className="h-3 w-3 rounded-full" style={{ backgroundColor: slice.colour }} aria-hidden="true" />
                    {slice.name}
                  </span>
                  {/* This is the share of the account. */}
                  <span className="tabular-nums text-slate-600">{((slice.value / totalValue) * 100).toFixed(1)}%</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* This card explains the numbers, supporting the study's market-literacy goal. */}
        <section className="rounded-xl border border-sky-100 bg-sky-50 p-5 text-sm text-slate-700 lg:col-span-2">
          <h2 className="flex items-center gap-2 font-semibold text-sky-800">
            <Info className="h-5 w-5" aria-hidden="true" />
            How these numbers work
          </h2>
          <dl className="mt-3 space-y-3">
            <div>
              <dt className="font-medium">Average buy price</dt>
              <dd>The average you paid per share across all your purchases of that stock.</dd>
            </div>
            <div>
              <dt className="font-medium">Unrealised profit / loss</dt>
              <dd>(Current price − average buy price) × shares held. It is only on paper until you sell.</dd>
            </div>
            <div>
              <dt className="font-medium">Realised profit / loss</dt>
              <dd>(Sell price − average buy price) × shares sold. It is locked in once you sell.</dd>
            </div>
            <div>
              <dt className="font-medium">Diversification</dt>
              <dd>Spreading money across several stocks reduces the damage if one company does badly.</dd>
            </div>
          </dl>
        </section>
      </div>

      {/* This card is the full holdings table. */}
      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-5 py-4">
          <h2 className="font-semibold">Holdings</h2>
        </div>
        {positions.length === 0 ? (
          // This is shown before the first purchase.
          <p className="px-5 py-10 text-center text-sm text-slate-500">You don&apos;t own any shares yet. All {formatKES(portfolio.cash_balance)} is in cash.</p>
        ) : (
          // This lets the table scroll sideways on phones.
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              {/* These are the column headings. */}
              <thead className="text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-medium">Stock</th>
                  <th className="px-5 py-3 text-right font-medium">Shares</th>
                  <th className="px-5 py-3 text-right font-medium">Avg buy price</th>
                  <th className="px-5 py-3 text-right font-medium">Current price</th>
                  <th className="px-5 py-3 text-right font-medium">Cost</th>
                  <th className="px-5 py-3 text-right font-medium">Value</th>
                  <th className="px-5 py-3 text-right font-medium">Profit / loss</th>
                  <th className="px-5 py-3 text-right font-medium">Weight</th>
                </tr>
              </thead>
              {/* These are the holdings, largest first. */}
              <tbody className="divide-y divide-slate-100">
                {positions.map((position) => (
                  <tr key={position.ticker} className="hover:bg-slate-50">
                    {/* This is the ticker and company. */}
                    <td className="px-5 py-3">
                      <p className="font-semibold">{position.ticker}</p>
                      <p className="text-xs text-slate-500">{position.company_name}</p>
                    </td>
                    <td className="px-5 py-3 text-right tabular-nums">{position.shares_held.toLocaleString("en-KE")}</td>
                    <td className="px-5 py-3 text-right tabular-nums">{formatKES(position.average_buy_price)}</td>
                    <td className="px-5 py-3 text-right tabular-nums">{formatKES(position.current_price)}</td>
                    <td className="px-5 py-3 text-right tabular-nums">{formatKES(position.cost_basis)}</td>
                    <td className="px-5 py-3 text-right font-medium tabular-nums">{formatKES(position.market_value)}</td>
                    {/* This is the paper profit or loss in KES and percent. */}
                    <td className={`px-5 py-3 text-right tabular-nums ${changeColor(position.unrealized_pnl)}`}>
                      <p>{formatSignedKES(position.unrealized_pnl)}</p>
                      <p className="text-xs">{formatPercent(position.unrealized_pnl_percent)}</p>
                    </td>
                    {/* This is the share of the whole account in this stock. */}
                    <td className="px-5 py-3 text-right tabular-nums text-slate-600">{((Number(position.market_value) / totalValue) * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
