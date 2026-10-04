// This imports useState to track the request in flight.
import { useState } from "react";
// This imports the star icon.
import { Star } from "lucide-react";
// This imports toast for confirmation pop-ups.
import toast from "react-hot-toast";
// This imports the API client and error helper.
import api, { getErrorMessage } from "../services/api";

// This is a star button that adds or removes a stock from the watchlist.
export default function WatchlistStar({ ticker, isWatched, onToggle, size = "h-5 w-5" }) {
  // This is true while the request runs, to block double clicks.
  const [isBusy, setIsBusy] = useState(false);

  // This runs when the star is clicked.
  const handleClick = async (event) => {
    // The star often sits inside a clickable card, so the click must not open the card too.
    event.preventDefault();
    // This stops the click reaching the card underneath.
    event.stopPropagation();
    // This blocks further clicks.
    setIsBusy(true);
    // This sends the change.
    try {
      // Starred stocks are removed; others are added.
      if (isWatched) await api.delete(`/watchlist/${ticker}`);
      else await api.post("/watchlist", { ticker });
      // This tells the parent page the new state.
      onToggle(ticker, !isWatched);
      // This confirms the change.
      toast.success(isWatched ? `${ticker} removed from your watchlist.` : `${ticker} added to your watchlist.`);
    } catch (error) {
      // This shows what went wrong.
      toast.error(getErrorMessage(error));
    } finally {
      // This re-enables the star.
      setIsBusy(false);
    }
  };

  // This returns the button.
  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={isBusy}
      // aria-pressed tells screen readers whether the star is on.
      aria-pressed={isWatched}
      aria-label={isWatched ? `Remove ${ticker} from watchlist` : `Add ${ticker} to watchlist`}
      title={isWatched ? "Remove from watchlist" : "Add to watchlist"}
      className="rounded-full p-1.5 hover:bg-amber-50 disabled:opacity-50"
    >
      {/* A filled amber star means "on the watchlist". */}
      <Star className={`${size} ${isWatched ? "fill-amber-400 text-amber-400" : "text-slate-300"}`} aria-hidden="true" />
    </button>
  );
}
