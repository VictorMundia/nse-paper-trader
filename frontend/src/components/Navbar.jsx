// This imports the icons used in the navigation bar.
import { BarChart3, Briefcase, History, LayoutDashboard, LogOut, TrendingUp, UserRound } from "lucide-react";
// This imports NavLink, a link that knows whether it points at the current page.
import { NavLink, useNavigate } from "react-router-dom";
// This imports toast for the "logged out" message.
import toast from "react-hot-toast";
// This imports the login state and actions.
import { useAuth } from "../context/AuthContext";
// This imports the KES money formatter.
import { formatKES } from "../utils/format";

// These are the main pages in the navigation bar, in display order.
const NAV_ITEMS = [
  // The home page with an overview of the account.
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  // The list of NSE stocks to research and trade.
  { to: "/stocks", label: "Stocks", icon: BarChart3 },
  // The student's current holdings.
  { to: "/portfolio", label: "Portfolio", icon: Briefcase },
  // Every buy and sell the student has made.
  { to: "/history", label: "History", icon: History },
  // Profile details and change password.
  { to: "/account", label: "Account", icon: UserRound },
];

// This builds the Tailwind classes for a nav link, highlighting the current page.
function navLinkClass({ isActive }) {
  // Shared classes for every link.
  const base = "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors";
  // The active page is emerald; the others turn grey on hover.
  return isActive ? `${base} bg-emerald-50 text-emerald-700` : `${base} text-slate-600 hover:bg-slate-100`;
}

// This is the bar shown at the top of every logged-in page.
export default function Navbar() {
  // This reads the student's profile and the logout action.
  const { user, logout } = useAuth();
  // This lets us move to another page from code.
  const navigate = useNavigate();

  // This logs out, confirms it, and returns to the login page.
  const handleLogout = () => {
    // This forgets the token and profile.
    logout();
    // This confirms the logout.
    toast.success("You have been logged out.");
    // This goes to the login page.
    navigate("/login", { replace: true });
  };

  // This returns the navbar layout.
  return (
    // This is the white bar with a bottom border that stays at the top while scrolling.
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white">
      {/* This limits the width on large screens and wraps items on small ones. */}
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3">
        {/* This is the logo, which links to the dashboard. */}
        <NavLink to="/" className="flex items-center gap-2 text-lg font-bold text-emerald-700">
          {/* This is the logo icon. */}
          <TrendingUp className="h-6 w-6" aria-hidden="true" />
          {/* This is the app name. */}
          NSE Paper Trader
        </NavLink>
        {/* This is the list of page links; it scrolls sideways on narrow phones. */}
        <nav className="order-last flex w-full gap-1 overflow-x-auto md:order-none md:w-auto">
          {/* This draws one link per page. */}
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            // "end" makes Dashboard active only on "/", not on every page.
            <NavLink key={to} to={to} end={end} className={navLinkClass}>
              {/* This is the page icon. */}
              <Icon className="h-4 w-4" aria-hidden="true" />
              {/* This is the page name. */}
              {label}
            </NavLink>
          ))}
        </nav>
        {/* This pushes the account details to the right edge. */}
        <div className="ml-auto flex items-center gap-4">
          {/* This shows the name and cash balance; hidden on very small screens to save space. */}
          <div className="hidden text-right sm:block">
            {/* This is the student's name. */}
            <p className="text-sm font-medium">{user?.full_name}</p>
            {/* This is the virtual cash balance. */}
            <p className="text-xs text-slate-500">Cash: {formatKES(user?.virtual_balance)}</p>
          </div>
          {/* This is the logout button. */}
          <button
            // type="button" stops it from ever submitting a form.
            type="button"
            // This runs the logout when clicked.
            onClick={handleLogout}
            // This styles the button.
            className="flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            {/* This is the logout icon. */}
            <LogOut className="h-4 w-4" aria-hidden="true" />
            {/* This is the button text. */}
            Log out
          </button>
        </div>
      </div>
    </header>
  );
}
