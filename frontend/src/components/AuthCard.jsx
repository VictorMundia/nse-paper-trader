// This imports the icons for the logo and the feature list.
import { BarChart3, GraduationCap, ShieldCheck, TrendingUp, Wallet } from "lucide-react";

// These are the selling points shown on the left panel.
const FEATURES = [
  // Real market data.
  { icon: BarChart3, title: "Real NSE prices", text: "15 Nairobi Securities Exchange stocks, updated every 30 minutes in market hours." },
  // No risk.
  { icon: Wallet, title: "KES 100,000 virtual money", text: "Buy and sell shares with zero financial risk." },
  // Learning goal.
  { icon: GraduationCap, title: "Learn by doing", text: "Build investing confidence and market literacy over three weeks." },
  // Security.
  { icon: ShieldCheck, title: "Secure account", text: "Passwords are hashed with bcrypt and sessions use signed tokens." },
];

// This is the two-panel layout used by the login and register pages.
export default function AuthCard({ title, subtitle, children, footer }) {
  // This returns the layout.
  return (
    // Two columns on large screens; on phones only the form column shows.
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* This is the green introduction panel, hidden below the "lg" screen width. */}
      <aside className="hidden flex-col justify-between bg-gradient-to-br from-emerald-700 to-emerald-900 p-12 text-white lg:flex">
        {/* This is the logo and app name. */}
        <div className="flex items-center gap-2 text-2xl font-bold">
          <TrendingUp className="h-7 w-7" aria-hidden="true" />
          NSE Paper Trader
        </div>
        {/* This is the headline and feature list. */}
        <div>
          {/* This is the headline. */}
          <h2 className="text-3xl font-semibold leading-tight">Practise investing on the Nairobi Securities Exchange — without risking a shilling.</h2>
          {/* This is the feature list. */}
          <ul className="mt-10 space-y-6">
            {FEATURES.map(({ icon: Icon, title: featureTitle, text }) => (
              <li key={featureTitle} className="flex gap-4">
                {/* This is the feature icon in a translucent circle. */}
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white/10">
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </span>
                {/* This is the feature text. */}
                <div>
                  <p className="font-medium">{featureTitle}</p>
                  <p className="text-sm text-emerald-100">{text}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
        
        <p className="text-sm text-emerald-200"></p>
      </aside>

      {/* This is the form column, centred vertically and horizontally. */}
      <main className="flex items-center justify-center px-4 py-12">
        {/* This limits the form width. */}
        <div className="w-full max-w-md">
          {/* This logo only shows on phones, where the green panel is hidden. */}
          <div className="mb-6 flex items-center justify-center gap-2 text-2xl font-bold text-emerald-700 lg:hidden">
            <TrendingUp className="h-7 w-7" aria-hidden="true" />
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
      </main>
    </div>
  );
}
