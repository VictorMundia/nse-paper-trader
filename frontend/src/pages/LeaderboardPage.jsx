// This imports React hooks: useEffect to load data, useState to store it.
import { useEffect, useState } from "react";
// This imports the icons used on the page.
import { Info, Loader2, Medal, Trophy } from "lucide-react";
// This imports toast for error pop-ups.
import toast from "react-hot-toast";
// This imports the API client and error helper.
import api, { getErrorMessage } from "../services/api";
// This imports the formatting helpers.
import { changeColor, formatKES, formatPercent } from "../utils/format";

// These are the filter buttons; an empty value means everyone.
const LEVEL_FILTERS = [
  { value: "", label: "Everyone" },
  { value: "beginner", label: "Beginners" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
];

// These colour the medals for the top three places.
const MEDAL_COLOURS = { 1: "text-amber-500", 2: "text-slate-400", 3: "text-orange-700" };

// This page ranks students by total account value.
export default function LeaderboardPage() {
  // This is the selected experience level filter.
  const [level, setLevel] = useState("");
  // This holds the response from /api/leaderboard.
  const [board, setBoard] = useState(null);
  // This is true while loading.
  const [isLoading, setIsLoading] = useState(true);

  // This reloads whenever the filter changes.
  useEffect(() => {
    // This flag ignores a slow old response if the filter has changed again.
    let isCurrent = true;
    // This shows the loading state.
    setIsLoading(true);
    // This asks for the ranking; params adds ?level=... only when one is chosen.
    api
      .get("/leaderboard", { params: level ? { level } : {} })
      // This stores the result.
      .then(({ data }) => isCurrent && setBoard(data))
      // A 401 is already handled by the API client.
      .catch((error) => isCurrent && error.response?.status !== 401 && toast.error(getErrorMessage(error)))
      // This hides the loading state.
      .finally(() => isCurrent && setIsLoading(false));
    // This marks the request as stale when the filter changes.
    return () => {
      isCurrent = false;
    };
  }, [level]);

  // This returns the page layout.
  return (
    // This stacks the sections.
    <div className="space-y-6">
      {/* This is the title. */}
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold">
          <Trophy className="h-7 w-7 text-amber-500" aria-hidden="true" />
          Leaderboard
        </h1>
        <p className="mt-1 text-slate-500">Students ranked by total account value: cash plus shares at the latest NSE prices.</p>
      </div>

      {/* These are the experience level filter buttons. */}
      <div className="flex flex-wrap gap-1 rounded-lg bg-slate-100 p-1 sm:inline-flex" role="group" aria-label="Filter by experience level">
        {LEVEL_FILTERS.map((filter) => (
          <button
            key={filter.value}
            type="button"
            onClick={() => setLevel(filter.value)}
            aria-pressed={level === filter.value}
            className={`rounded-md px-4 py-1.5 text-sm font-medium ${level === filter.value ? "bg-white shadow-sm" : "text-slate-500 hover:text-slate-900"}`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {!board ? (
        // This is shown on the first load.
        <div className="flex h-40 items-center justify-center gap-3 text-slate-500">
          <Loader2 className="h-6 w-6 animate-spin" aria-hidden="true" />
          Loading leaderboard...
        </div>
      ) : (
        // The content fades while a new filter loads.
        <div className={`space-y-6 transition-opacity ${isLoading ? "opacity-50" : ""}`}>
          {/* This card shows the student's own position. */}
          <section className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
            {board.you ? (
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-sm text-emerald-800">Your rank{level && ` among ${LEVEL_FILTERS.find((f) => f.value === level).label.toLowerCase()}`}</p>
                  <p className="text-3xl font-bold text-emerald-900">
                    #{board.you.rank} <span className="text-base font-normal text-emerald-800">of {board.ranked_count}</span>
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xl font-semibold">{formatKES(board.you.total_value)}</p>
                  <p className={`text-sm font-medium ${changeColor(board.you.total_return)}`}>{formatPercent(board.you.total_return_percent)} return</p>
                </div>
              </div>
            ) : (
              // This is shown before the student's first trade, or if they are outside the selected level.
              <p className="text-sm text-emerald-900">You&apos;re not on this leaderboard yet. Make your first trade on the Stocks page to be ranked.</p>
            )}
          </section>

          {/* This card is the ranking table. */}
          <section className="rounded-xl border border-slate-200 bg-white">
            {board.entries.length === 0 ? (
              // This explains an empty leaderboard.
              <p className="px-5 py-10 text-center text-sm text-slate-500">No one has traded yet{level && " at this level"}. Be the first!</p>
            ) : (
              // This lets the table scroll sideways on phones.
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  {/* These are the column headings. */}
                  <thead className="text-left text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-5 py-3 font-medium">Rank</th>
                      <th className="px-5 py-3 font-medium">Student</th>
                      <th className="hidden px-5 py-3 font-medium sm:table-cell">Level</th>
                      <th className="px-5 py-3 text-right font-medium">Account value</th>
                      <th className="px-5 py-3 text-right font-medium">Return</th>
                      <th className="hidden px-5 py-3 text-right font-medium sm:table-cell">Trades</th>
                    </tr>
                  </thead>
                  {/* These are the ranked students. */}
                  <tbody className="divide-y divide-slate-100">
                    {board.entries.map((entry) => (
                      // The student's own row is highlighted.
                      <tr key={`${entry.rank}-${entry.display_name}-${entry.trade_count}`} className={entry.is_current_user ? "bg-emerald-50 font-medium" : "hover:bg-slate-50"}>
                        {/* The top three get a coloured medal. */}
                        <td className="px-5 py-3">
                          <span className="flex items-center gap-1.5 tabular-nums">
                            {MEDAL_COLOURS[entry.rank] && <Medal className={`h-4 w-4 ${MEDAL_COLOURS[entry.rank]}`} aria-hidden="true" />}
                            {entry.rank}
                          </span>
                        </td>
                        {/* This is the shortened name, with "(you)" on the student's own row. */}
                        <td className="px-5 py-3">
                          {entry.display_name}
                          {entry.is_current_user && <span className="ml-1 text-emerald-700">(you)</span>}
                        </td>
                        <td className="hidden px-5 py-3 capitalize text-slate-600 sm:table-cell">{entry.experience_level}</td>
                        <td className="px-5 py-3 text-right tabular-nums">{formatKES(entry.total_value)}</td>
                        <td className={`px-5 py-3 text-right tabular-nums ${changeColor(entry.total_return)}`}>{formatPercent(entry.total_return_percent)}</td>
                        <td className="hidden px-5 py-3 text-right tabular-nums text-slate-600 sm:table-cell">{entry.trade_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* This explains how the ranking works. */}
          <p className="flex items-start gap-2 text-xs text-slate-500">
            <Info className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            Only students who have made at least one trade are ranked. Equal account values share a rank. Names are shortened to protect privacy. Top 50 shown.
          </p>
        </div>
      )}
    </div>
  );
}
