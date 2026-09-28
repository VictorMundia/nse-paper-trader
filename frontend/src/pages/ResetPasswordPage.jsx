// This imports useState to hold what the student types.
import { useState } from "react";
// This imports router tools: Link for links, useNavigate to redirect, useSearchParams to read ?token= from the URL.
import { Link, useNavigate, useSearchParams } from "react-router-dom";
// This imports toast for success and error pop-ups.
import toast from "react-hot-toast";
// This imports the shared card layout.
import AuthCard from "../components/AuthCard";
// This imports the login state so a logged-in visitor is logged out after the reset.
import { useAuth } from "../context/AuthContext";
// This imports the API client and error helper.
import api, { getErrorMessage } from "../services/api";

// These are the Tailwind classes for the inputs.
const inputClass =
  "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200";

// This page is opened from the reset email and sets a new password.
export default function ResetPasswordPage() {
  // This reads the query string of the current URL.
  const [searchParams] = useSearchParams();
  // This is the one-time token from the email link.
  const token = searchParams.get("token");
  // This holds the new password.
  const [password, setPassword] = useState("");
  // This holds the confirmation.
  const [confirmPassword, setConfirmPassword] = useState("");
  // This is true while the request is in flight.
  const [isSubmitting, setIsSubmitting] = useState(false);
  // This reads the logout action.
  const { logout } = useAuth();
  // This lets us redirect after the reset.
  const navigate = useNavigate();

  // This runs when the form is submitted.
  const handleSubmit = async (event) => {
    // This stops the browser from reloading the page.
    event.preventDefault();
    // This catches typos before contacting the server.
    if (password !== confirmPassword) {
      // This explains the problem.
      toast.error("The two passwords do not match.");
      // This stops here.
      return;
    }
    // This disables the button.
    setIsSubmitting(true);
    // This sends the reset.
    try {
      // This sends the token and the new password.
      const { data } = await api.post("/auth/reset-password", { token, new_password: password });
      // Every old session is now invalid on the server, so any local one is cleared too.
      logout();
      // This confirms success.
      toast.success(data.message);
      // This opens the login page.
      navigate("/login", { replace: true });
    } catch (error) {
      // This shows the server's message, e.g. an expired link.
      toast.error(getErrorMessage(error));
      // This re-enables the button.
      setIsSubmitting(false);
    }
  };

  // This returns the page layout.
  return (
    <AuthCard
      // This is the card title.
      title="Choose a new password"
      // This is the line under the title.
      subtitle="Reset links work once and expire 30 minutes after they are sent."
      // This is the link below the card.
      footer={
        <Link to="/forgot-password" className="font-medium text-emerald-700 hover:underline">
          Request a new link
        </Link>
      }
    >
      {!token ? (
        // This is shown if the page is opened without a token.
        <p className="rounded-lg bg-rose-50 p-4 text-sm text-rose-700">This reset link is incomplete. Please open the full link from your email, or request a new one.</p>
      ) : (
        // This is the new password form.
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* This is the new password field. */}
          <label className="block text-sm font-medium">
            New password
            <input type="password" autoComplete="new-password" required minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} className={inputClass} />
            <span className="mt-1 block text-xs font-normal text-slate-500">At least 8 characters.</span>
          </label>
          {/* This is the confirmation field. */}
          <label className="block text-sm font-medium">
            Confirm new password
            <input type="password" autoComplete="new-password" required minLength={8} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} className={inputClass} />
          </label>
          {/* This is the submit button. */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-emerald-600 py-2.5 font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? "Saving..." : "Save new password"}
          </button>
        </form>
      )}
    </AuthCard>
  );
}
