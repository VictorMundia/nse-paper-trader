// This imports the logo icon.
import { TrendingUp } from "lucide-react";

// This is the centred card used by the login and register pages.
export default function AuthCard({ title, subtitle, children, footer }) {
  // This returns the card layout.
  return (
    // This centres the card on the screen.
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      {/* This limits the card width. */}
      <div className="w-full max-w-md">
        {/* This is the logo and app name above the card. */}
        <div className="mb-6 flex items-center justify-center gap-2 text-2xl font-bold text-emerald-700">
          {/* This is the logo icon. */}
          <TrendingUp className="h-7 w-7" aria-hidden="true" />
          {/* This is the app name. */}
          NSE Paper Trader
        </div>
        {/* This is the white card. */}
        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          {/* This is the card title. */}
          <h1 className="text-xl font-semibold">{title}</h1>
          {/* This is the line under the title. */}
          <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
          {/* This is the form. */}
          <div className="mt-6">{children}</div>
        </div>
        {/* This is the link below the card, e.g. "No account? Register". */}
        <p className="mt-6 text-center text-sm text-slate-600">{footer}</p>
      </div>
    </div>
  );
}
