// This imports useState to hold what the student types.
import { useState } from "react";
// This imports the icons used on the page.
import { KeyRound, UserRound } from "lucide-react";
// This imports toast for success and error pop-ups.
import toast from "react-hot-toast";
// This imports the logged-in student's profile.
import { useAuth } from "../context/AuthContext";
// This imports the API client, the token storage, and the error helper.
import api, { getErrorMessage, tokenStorage } from "../services/api";
// This imports the date formatter.
import { formatEAT } from "../utils/format";

// These are the Tailwind classes for the inputs.
const inputClass =
  "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200";

// This is the empty state of the form, used on first load and after a successful change.
const EMPTY_FORM = { current_password: "", new_password: "", confirm_password: "" };

// This page shows account details and lets the student change their password.
export default function AccountPage() {
  // This reads the student's profile.
  const { user } = useAuth();
  // This holds the three password fields.
  const [form, setForm] = useState(EMPTY_FORM);
  // This is true while the request is in flight.
  const [isSubmitting, setIsSubmitting] = useState(false);

  // This updates whichever field changed, using the input's name attribute.
  const handleChange = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  // This runs when the form is submitted.
  const handleSubmit = async (event) => {
    // This stops the browser from reloading the page.
    event.preventDefault();
    // This catches typos before contacting the server.
    if (form.new_password !== form.confirm_password) {
      // This explains the problem.
      toast.error("The two new passwords do not match.");
      // This stops here.
      return;
    }
    // This disables the button.
    setIsSubmitting(true);
    // This sends the change.
    try {
      // This sends the current and new passwords.
      const { data } = await api.post("/auth/change-password", { current_password: form.current_password, new_password: form.new_password });
      // The old token is now rejected by the server, so the fresh one keeps this device logged in.
      tokenStorage.set(data.access_token);
      // This clears the form.
      setForm(EMPTY_FORM);
      // This confirms success and explains the effect on other devices.
      toast.success("Password changed. Any other devices have been logged out.");
    } catch (error) {
      // This shows the server's message, e.g. "Current password is incorrect."
      toast.error(getErrorMessage(error));
    } finally {
      // This re-enables the button.
      setIsSubmitting(false);
    }
  };

  // This returns the page layout.
  return (
    // This stacks the two cards.
    <div className="max-w-2xl space-y-6">
      {/* This is the page title. */}
      <h1 className="text-2xl font-bold">Account</h1>

      {/* This card shows the profile. */}
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        {/* This is the card heading. */}
        <h2 className="flex items-center gap-2 font-semibold">
          <UserRound className="h-5 w-5 text-emerald-600" aria-hidden="true" />
          Profile
        </h2>
        {/* This is a two-column list of details. */}
        <dl className="mt-4 grid gap-4 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-slate-500">Full name</dt>
            <dd className="font-medium">{user.full_name}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Email</dt>
            <dd className="font-medium">{user.email}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Experience level</dt>
            <dd className="font-medium capitalize">{user.experience_level}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Member since</dt>
            <dd className="font-medium">{formatEAT(user.created_at)} EAT</dd>
          </div>
        </dl>
      </section>

      {/* This card holds the change password form. */}
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        {/* This is the card heading. */}
        <h2 className="flex items-center gap-2 font-semibold">
          <KeyRound className="h-5 w-5 text-emerald-600" aria-hidden="true" />
          Change password
        </h2>
        {/* This explains the effect on other devices. */}
        <p className="mt-1 text-sm text-slate-500">Changing your password logs you out on every other device.</p>
        {/* This is the form. */}
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {/* This is the current password field. */}
          <label className="block text-sm font-medium">
            Current password
            <input name="current_password" type="password" autoComplete="current-password" required value={form.current_password} onChange={handleChange} className={inputClass} />
          </label>
          {/* This is the new password field. */}
          <label className="block text-sm font-medium">
            New password
            <input name="new_password" type="password" autoComplete="new-password" required minLength={8} value={form.new_password} onChange={handleChange} className={inputClass} />
            <span className="mt-1 block text-xs font-normal text-slate-500">At least 8 characters.</span>
          </label>
          {/* This is the confirmation field. */}
          <label className="block text-sm font-medium">
            Confirm new password
            <input name="confirm_password" type="password" autoComplete="new-password" required minLength={8} value={form.confirm_password} onChange={handleChange} className={inputClass} />
          </label>
          {/* This is the submit button. */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-lg bg-emerald-600 px-5 py-2.5 font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? "Saving..." : "Change password"}
          </button>
        </form>
      </section>
    </div>
  );
}
