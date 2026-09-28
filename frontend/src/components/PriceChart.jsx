// This imports React hooks: useEffect to load data, useState to store it.
import { useEffect, useState } from "react";
// This imports the Recharts pieces used to draw a line chart.
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
// This imports the spinner icon.
import { Loader2 } from "lucide-react";
// This imports the shared API client and error helper.
import api, { getErrorMessage } from "../services/api";
// This imports the formatting helpers.
import { formatEAT, formatKES, formatPercent, changeColor, parseUtc } from "../utils/format";

// These are the time ranges the student can pick.
const RANGES = [
  // The last day of prices.
  { days: 1, label: "1D" },
  // The last week.
  { days: 7, label: "1W" },
  // The last month.
  { days: 30, label: "1M" },
];

// This shows the price history of one stock as a line chart.
export default function PriceChart({ ticker, companyName }) {
  // This is the selected time range in days.
  const [days, setDays] = useState(7);
  // This holds the chart points.
  const [points, setPoints] = useState([]);
  // This is true while the history loads.
  const [isLoading, setIsLoading] = useState(true);
  // This holds an error message if loading fails.
  const [error, setError] = useState(null);

  // This reloads the history whenever the stock or the range changes.
  useEffect(() => {
    // This flag ignores a slow old response if the student has already picked another stock.
    let isCurrent = true;
    // This shows the spinner.
    setIsLoading(true);
    // This asks the backend for the price history.
    api
      .get(`/stocks/${ticker}/prices`, { params: { days } })
      // This converts each row into a chart point.
      .then(({ data }) => {
        // This skips the update if a newer request has started.
        if (!isCurrent) return;
        // Recharts needs numbers, and a timestamp for the x-axis.
        setPoints(data.prices.map((row) => ({ time: parseUtc(row.recorded_at).getTime(), price: Number(row.price), recorded_at: row.recorded_at })));
        // This clears any earlier error.
        setError(null);
      })
      // This stores a readable error.
      .catch((err) => isCurrent && setError(getErrorMessage(err)))
      // This hides the spinner.
      .finally(() => isCurrent && setIsLoading(false));
    // This marks the request as stale when the stock or range changes.
    return () => {
      isCurrent = false;
    };
  }, [ticker, days]);

  // This is the first price in the range.
  const first = points[0]?.price;
  // This is the latest price in the range.
  const last = points[points.length - 1]?.price;
  // This is the percentage change across the range.
  const rangeChange = first && last ? ((last - first) / first) * 100 : null;
  // Green line for a rise, red for a fall.
  const lineColor = rangeChange < 0 ? "#e11d48" : "#059669";

  // This returns the chart card.
  return (
    // This is the white card.
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      {/* This header holds the stock name, change, and range buttons. */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        {/* This is the stock name and latest price. */}
        <div>
          {/* This is the ticker and company. */}
          <h2 className="font-semibold">
            {ticker} <span className="font-normal text-slate-500">· {companyName}</span>
          </h2>
          {/* This is the latest price and the change across the range. */}
          <p className="mt-1 text-2xl font-semibold">
            {formatKES(last)}{" "}
            <span className={`text-sm font-medium ${changeColor(rangeChange)}`}>{formatPercent(rangeChange)}</span>
          </p>
        </div>
        {/* These are the range buttons. */}
        <div className="flex gap-1 rounded-lg bg-slate-100 p-1">
          {RANGES.map((range) => (
            // The selected range is highlighted in white.
            <button
              key={range.days}
              type="button"
              onClick={() => setDays(range.days)}
              className={`rounded-md px-3 py-1 text-sm font-medium ${days === range.days ? "bg-white shadow-sm" : "text-slate-500 hover:text-slate-900"}`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>
      {/* This fixed-height area holds the chart, spinner, or message. */}
      <div className="mt-4 h-64">
        {isLoading ? (
          // This is shown while loading.
          <div className="flex h-full items-center justify-center text-slate-400">
            <Loader2 className="h-6 w-6 animate-spin" aria-hidden="true" />
          </div>
        ) : error ? (
          // This is shown if loading failed.
          <p className="flex h-full items-center justify-center text-rose-600">{error}</p>
        ) : points.length < 2 ? (
          // A line needs at least two points.
          <p className="flex h-full items-center justify-center text-slate-500">Not enough price history yet for this range.</p>
        ) : (
          // ResponsiveContainer makes the chart fill the box at any screen width.
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points} margin={{ top: 5, right: 10, bottom: 0, left: 0 }}>
              {/* These are faint horizontal grid lines. */}
              <CartesianGrid stroke="#e2e8f0" vertical={false} />
              {/* The x-axis is time, labelled in Nairobi time. */}
              <XAxis dataKey="time" type="number" scale="time" domain={["dataMin", "dataMax"]} tickFormatter={(time) => formatEAT(new Date(time).toISOString())} tick={{ fontSize: 12, fill: "#64748b" }} minTickGap={40} />
              {/* The y-axis is price, with a little padding above and below. */}
              <YAxis domain={["auto", "auto"]} tick={{ fontSize: 12, fill: "#64748b" }} width={60} tickFormatter={(price) => price.toFixed(2)} />
              {/* This shows the exact price and time when hovering. */}
              <Tooltip formatter={(price) => [formatKES(price), "Price"]} labelFormatter={(time) => formatEAT(new Date(time).toISOString())} />
              {/* "linear" draws straight lines between real prices; smoothed curves would invent prices that never happened. */}
              <Line type="linear" dataKey="price" stroke={lineColor} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
