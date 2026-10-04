// This shows a coloured BUY (green) or SELL (red) label for a trade.
export default function TradeTypeBadge({ type }) {
  // This picks the colours for the trade type.
  const colours = type === "BUY" ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700";
  // This returns the badge.
  return <span className={`inline-block rounded px-2 py-0.5 text-xs font-semibold ${colours}`}>{type}</span>;
}
