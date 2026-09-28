// This imports the formatting helpers.
import { changeColor, formatEAT, formatKES, formatPercent } from "../utils/format";

// This formats share volume with thousands separators, e.g. 1,290,262.
const volumeFormatter = new Intl.NumberFormat("en-KE");

// This lists all tracked NSE stocks; clicking a row shows its chart.
export default function MarketTable({ stocks, selectedTicker, onSelect }) {
  // This finds the newest update time across all stocks.
  const lastUpdated = stocks.reduce((latest, stock) => (stock.last_updated > latest ? stock.last_updated : latest), "");

  // This returns the table card.
  return (
    // This is the white card.
    <div className="rounded-xl border border-slate-200 bg-white">
      {/* This is the card header. */}
      <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-slate-200 px-5 py-4">
        {/* This is the title. */}
        <h2 className="font-semibold">NSE market</h2>
        {/* This shows when prices were last scraped, in Nairobi time. */}
        <p className="text-xs text-slate-500">Prices from afx.kwayisi.org · updated {formatEAT(lastUpdated)} EAT</p>
      </div>
      {/* This lets the table scroll sideways on narrow phones. */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          {/* These are the column headings. */}
          <thead className="text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-5 py-3 font-medium">Stock</th>
              <th className="px-5 py-3 text-right font-medium">Price</th>
              <th className="px-5 py-3 text-right font-medium">Change</th>
              <th className="hidden px-5 py-3 text-right font-medium sm:table-cell">Volume</th>
            </tr>
          </thead>
          {/* These are the stock rows. */}
          <tbody className="divide-y divide-slate-100">
            {stocks.map((stock) => (
              // Clicking a row selects it for the chart; the selected row is tinted.
              <tr
                key={stock.ticker}
                onClick={() => onSelect(stock)}
                className={`cursor-pointer hover:bg-slate-50 ${stock.ticker === selectedTicker ? "bg-emerald-50" : ""}`}
              >
                {/* This is the ticker and company name. */}
                <td className="px-5 py-3">
                  <p className="font-semibold">{stock.ticker}</p>
                  <p className="text-xs text-slate-500">{stock.company_name}</p>
                </td>
                {/* This is the latest price. */}
                <td className="px-5 py-3 text-right font-medium tabular-nums">{formatKES(stock.price)}</td>
                {/* This is the change since the previous update, green or red. */}
                <td className={`px-5 py-3 text-right tabular-nums ${changeColor(stock.change)}`}>{formatPercent(stock.change_percent)}</td>
                {/* This is the traded volume; hidden on phones to save space. */}
                <td className="hidden px-5 py-3 text-right tabular-nums text-slate-500 sm:table-cell">
                  {stock.volume === null ? "—" : volumeFormatter.format(stock.volume)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
