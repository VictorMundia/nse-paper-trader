// This imports the icons for the summary cards.
import { GraduationCap, Wallet } from "lucide-react";
// This imports the logged-in student's profile.
import { useAuth } from "../context/AuthContext";
// This imports the KES money formatter.
import { formatKES } from "../utils/format";
// This imports the "coming soon" block.
import PlaceholderPage from "../components/PlaceholderPage";

// This is the home page after login.
export default function DashboardPage() {
  // This reads the student's profile from /auth/me.
  const { user } = useAuth();

  // This returns the page layout.
  return (
    // This stacks the sections with space between them.
    <div className="space-y-8">
      {/* This is the greeting. */}
      <div>
        {/* This greets the student by first name. */}
        <h1 className="text-2xl font-bold">Hello, {user.full_name.split(" ")[0]}</h1>
        {/* This reminds them the money is virtual. */}
        <p className="mt-1 text-slate-500">Here is your virtual trading account.</p>
      </div>
      {/* These are two summary cards side by side on wider screens. */}
      <div className="grid gap-4 sm:grid-cols-2">
        {/* This card shows the cash balance. */}
        <div className="flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-5">
          {/* This is the wallet icon. */}
          <Wallet className="h-8 w-8 text-emerald-600" aria-hidden="true" />
          {/* This is the label and value. */}
          <div>
            <p className="text-sm text-slate-500">Cash available</p>
            <p className="text-xl font-semibold">{formatKES(user.virtual_balance)}</p>
          </div>
        </div>
        {/* This card shows the experience level chosen at registration. */}
        <div className="flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-5">
          {/* This is the graduation cap icon. */}
          <GraduationCap className="h-8 w-8 text-sky-600" aria-hidden="true" />
          {/* This is the label and value. */}
          <div>
            <p className="text-sm text-slate-500">Experience level</p>
            {/* "capitalize" shows "beginner" as "Beginner". */}
            <p className="text-xl font-semibold capitalize">{user.experience_level ?? "Not set"}</p>
          </div>
        </div>
      </div>
      {/* This marks where the full dashboard will go. */}
      <PlaceholderPage title="Portfolio overview" description="Charts of your portfolio value, holdings, and recent trades." phase={7} />
    </div>
  );
}
