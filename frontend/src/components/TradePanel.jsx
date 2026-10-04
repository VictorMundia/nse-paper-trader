// This imports useState to hold the form state.
import { useState } from "react";
// This imports the icons used in the panel.
import { AlertCircle, Info } from "lucide-react";
// This imports toast for result pop-ups.
import toast from "react-hot-toast";
// This imports the API client and error helper.
import api, { getErrorMessage } from "../services/api";
// This imports the money formatter.
import { formatKES } from "../utils/format";

// This is the Buy/Sell panel on a stock's detail page.
export default function TradePanel({ stock, cash, sharesHeld, onTraded }) {
  // This is the selected side: "BUY" or "SELL".
  const [side, setSide] = useState("BUY");
  // The quantity is kept as typed text so we can spot invalid input such as "2.5".
  const [quantityText, setQuantityText] = useState("");
  // This is true on the "Review your order" step.
  const [isReviewing, setIsReviewing] = useState(false);
  // This is true while the order is being sent.
  const [isSubmitting, setIsSubmitting] = useState(false);

  // This is the latest price as a number, for the preview only; the server decides the real price.
  const price = Number(stock.price);
  // Only whole numbers count; anything else becomes 0 and shows an error.
  const quantity = /^\d+$/.test(quantityText) ? Number(quantityText) : 0;
  // This is the estimated cost or proceeds.
  const estimatedTotal = price * quantity;
  // This is the most the student can buy with their cash, or sell from their holding.
  const maxQuantity = side === "BUY" ? Math.floor(Number(cash) / price) : sharesHeld;
  // This is true when the student is buying.
  const isBuy = side === "BUY";

  // This works out what, if anything, is wrong with the order.
  let problem = null;
  // Text was typed but it is not a positive whole number.
  if (quantityText && quantity < 1) problem = "Enter a whole number of shares, 1 or more.";
  // The purchase costs more than the cash available.
  else if (isBuy && estimatedTotal > Number(cash)) problem = `Not enough cash. You can afford up to ${maxQuantity.toLocaleString("en-KE")} shares.`;
  // The sale is larger than the holding.
  else if (!isBuy && quantity > sharesHeld) problem = `You only hold ${sharesHeld.toLocaleString("en-KE")} shares.`;
  // This is true when the order can go to the review step.
  const canReview = quantity >= 1 && !problem;

  // This switches between Buy and Sell and starts a fresh order.
  const switchSide = (newSide) => {
    // This sets the side.
    setSide(newSide);
    // This clears the quantity.
    setQuantityText("");
    // This leaves the review step.
    setIsReviewing(false);
  };

  // This sends the order after the student confirms it.
  const placeOrder = async () => {
    // This disables the buttons.
    setIsSubmitting(true);
    // This sends the order.
    try {
      // This calls /api/trades/buy or /api/trades/sell.
      const { data } = await api.post(`/trades/${isBuy ? "buy" : "sell"}`, { ticker: stock.ticker, quantity });
      // This confirms the real execution price and total from the server.
      toast.success(
        `${isBuy ? "Bought" : "Sold"} ${data.trade.quantity.toLocaleString("en-KE")} ${data.trade.ticker} at ${formatKES(data.trade.price_at_trade)} — total ${formatKES(data.trade.total_value)}`,
        { duration: 6000 },
      );
      // This clears the form.
      setQuantityText("");
      // This tells the page to reload cash, holdings, and the navbar balance.
      onTraded();
    } catch (error) {
      // This shows the server's reason, e.g. "Insufficient funds: ...".
      toast.error(getErrorMessage(error));
    } finally {
      // This leaves the review step and re-enables the buttons.
      setIsReviewing(false);
      // This re-enables the buttons.
      setIsSubmitting(false);
    }
  };

  // This returns the panel.
  return (
    // This is the white card.
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      {/* These are the Buy and Sell tabs. */}
      <div className="grid grid-cols-2 gap-1 rounded-lg bg-slate-100 p-1" role="group" aria-label="Order side">
        {["BUY", "SELL"].map((option) => (
          // The selected tab is green for Buy and red for Sell.
          <button
            key={option}
            type="button"
            onClick={() => switchSide(option)}
            aria-pressed={side === option}
            className={`rounded-md py-2 text-sm font-semibold ${side === option ? (option === "BUY" ? "bg-emerald-600 text-white" : "bg-rose-600 text-white") : "text-slate-600 hover:text-slate-900"}`}
          >
            {option === "BUY" ? "Buy" : "Sell"}
          </button>
        ))}
      </div>

      {/* This shows what the student has to work with. */}
      <p className="mt-4 text-sm text-slate-500">
        {isBuy ? (
          <>Cash available: <span className="font-medium text-slate-900">{formatKES(cash)}</span></>
        ) : (
          <>You hold: <span className="font-medium text-slate-900">{sharesHeld.toLocaleString("en-KE")} shares</span></>
        )}
      </p>

      {!isBuy && sharesHeld === 0 ? (
        // There is nothing to sell yet.
        <p className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-600">You don&apos;t own any {stock.ticker} shares yet. Buy some first.</p>
      ) : isReviewing ? (
        // This is the review step: one last look before the order is sent.
        <div className="mt-4 space-y-4">
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm">
            <p className="font-semibold">Review your order</p>
            <dl className="mt-3 space-y-1.5">
              <div className="flex justify-between"><dt className="text-slate-500">Action</dt><dd className="font-medium">{isBuy ? "Buy" : "Sell"} {stock.ticker}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">Shares</dt><dd className="font-medium tabular-nums">{quantity.toLocaleString("en-KE")}</dd></div>
              <div className="flex justify-between"><dt className="text-slate-500">Price (approx.)</dt><dd className="font-medium tabular-nums">{formatKES(price)}</dd></div>
              <div className="flex justify-between border-t border-slate-200 pt-1.5"><dt className="font-medium">{isBuy ? "Estimated cost" : "Estimated proceeds"}</dt><dd className="font-semibold tabular-nums">{formatKES(estimatedTotal)}</dd></div>
            </dl>
          </div>
          {/* These are the cancel and confirm buttons. */}
          <div className="grid grid-cols-2 gap-2">
            <button type="button" onClick={() => setIsReviewing(false)} disabled={isSubmitting} className="rounded-lg border border-slate-300 py-2.5 text-sm font-medium hover:bg-slate-50 disabled:opacity-60">
              Back
            </button>
            <button
              type="button"
              onClick={placeOrder}
              disabled={isSubmitting}
              className={`rounded-lg py-2.5 text-sm font-semibold text-white disabled:opacity-60 ${isBuy ? "bg-emerald-600 hover:bg-emerald-700" : "bg-rose-600 hover:bg-rose-700"}`}
            >
              {isSubmitting ? "Placing order..." : `Confirm ${isBuy ? "buy" : "sell"}`}
            </button>
          </div>
        </div>
      ) : (
        // This is the order form.
        <form
          // Submitting the form moves to the review step instead of trading straight away.
          onSubmit={(event) => {
            // This stops the page reloading.
            event.preventDefault();
            // This opens the review step if the order is valid.
            if (canReview) setIsReviewing(true);
          }}
          className="mt-4 space-y-4"
        >
          {/* This is the quantity field with a "Max" shortcut. */}
          <label className="block text-sm font-medium">
            Number of shares
            <div className="mt-1 flex gap-2">
              {/* inputMode="numeric" shows a number keypad on phones while still letting us validate the text. */}
              <input
                type="text"
                inputMode="numeric"
                autoComplete="off"
                placeholder="e.g. 100"
                value={quantityText}
                onChange={(event) => setQuantityText(event.target.value.trim())}
                aria-invalid={Boolean(problem)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
              />
              {/* This fills in the largest possible quantity. */}
              <button
                type="button"
                onClick={() => setQuantityText(String(maxQuantity))}
                disabled={maxQuantity < 1}
                className="rounded-lg border border-slate-300 px-3 text-sm font-medium hover:bg-slate-50 disabled:opacity-50"
              >
                Max
              </button>
            </div>
          </label>

          {/* This shows the estimate or the problem. */}
          {problem ? (
            <p className="flex items-start gap-2 text-sm text-rose-600">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              {problem}
            </p>
          ) : (
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">{isBuy ? "Estimated cost" : "Estimated proceeds"}</span>
              <span className="font-semibold tabular-nums">{formatKES(estimatedTotal)}</span>
            </div>
          )}

          {/* This is the review button. */}
          <button
            type="submit"
            disabled={!canReview}
            className={`w-full rounded-lg py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50 ${isBuy ? "bg-emerald-600 hover:bg-emerald-700" : "bg-rose-600 hover:bg-rose-700"}`}
          >
            Review {isBuy ? "buy" : "sell"} order
          </button>
        </form>
      )}

      {/* This explains how orders work, supporting the study's learning goal. */}
      <p className="mt-4 flex items-start gap-2 text-xs text-slate-500">
        <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
        Market order: it executes instantly at the latest NSE price, which can differ slightly from the estimate if prices update. No fees are charged.
      </p>
    </section>
  );
}
