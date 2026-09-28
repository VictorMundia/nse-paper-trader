// This imports useState to hold what the student types.
import { useState } from "react";
// This imports router tools: Link for the register link, useNavigate to redirect, useLocation to read where they came from.
import { Link, useLocation, useNavigate } from "react-router-dom";
// This imports toast for success and error pop-ups.
import toast from "react-hot-toast";
// This imports the shared card layout.
import AuthCard from "../components/AuthCard";
// This imports the login action.
import { useAuth } from "../context/AuthContext";
// This imports the helper that turns API errors into readable text.
import { getErrorMessage } from "../services/api";

// These are the Tailwind classes shared by every text input.
const inputClass =
  "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200";

// This is the login page.
export default function LoginPage() {
  // This holds the email typed so far.
  const [email, setEmail] = useState("");
  // This holds the password typed so far.
  const [password, setPassword] = useState("");
  // This is true while the request is in flight, to stop double submission.
  const [isSubmitting, setIsSubmitting] = useState(false);
  // This reads the login action.
  const { login } = useAuth();
  // This lets us redirect after login.
  const navigate = useNavigate();
  // This reads the page ProtectedRoute remembered, so we can send the student back there.
  const location = useLocation();
  // This is where to go after login: the remembered page, or the dashboard.
  const redirectTo = location.state?.from?.pathname ?? "/";

  // This runs when the form is submitted.
  const handleSubmit = async (event) => {
    // This stops the browser from reloading the page, its default form behaviour.
    event.preventDefault();
    // This disables the button.
    setIsSubmitting(true);
    // This attempts the login.
    try {
      // This sends the credentials and loads the profile.
      const user = await login(email, password);
      // This greets the student by first name.
      toast.success(`Welcome back, ${user.full_name.split(" ")[0]}!`);
      // This opens the page they wanted; replace stops "Back" returning to the login form.
      navigate(redirectTo, { replace: true });
    } catch (error) {
      // This shows the backend's message, e.g. "Invalid email or password."
      toast.error(getErrorMessage(error));
      // This re-enables the button so they can try again.
      setIsSubmitting(false);
    }
  };

  // This returns the page layout.
  return (
    // This wraps the form in the shared card.
    <AuthCard
      // This is the card title.
      title="Log in"
      // This is the line under the title.
      subtitle="Trade NSE shares with KES 100,000 in virtual money."
      // This is the link below the card.
      footer={
        <>
          No account yet?{" "}
          <Link to="/register" className="font-medium text-emerald-700 hover:underline">
            Create one
          </Link>
        </>
      }
    >
      {/* This is the login form. */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* This is the email field; the label is linked to the input for screen readers. */}
        <label className="block text-sm font-medium">
          Email
          <input
            // type="email" gives phones the @ keyboard and basic format checking.
            type="email"
            // This lets the browser offer saved emails.
            autoComplete="email"
            // The browser blocks submission if this is empty.
            required
            // This shows the current value.
            value={email}
            // This saves each keystroke.
            onChange={(event) => setEmail(event.target.value)}
            // This styles the input.
            className={inputClass}
          />
        </label>
        {/* This is the password field. */}
        <label className="block text-sm font-medium">
          Password
          <input
            // type="password" hides the characters.
            type="password"
            // This lets password managers fill it in.
            autoComplete="current-password"
            // The browser blocks submission if this is empty.
            required
            // This shows the current value.
            value={password}
            // This saves each keystroke.
            onChange={(event) => setPassword(event.target.value)}
            // This styles the input.
            className={inputClass}
          />
        </label>
        {/* This is the submit button. */}
        <button
          // This submits the form.
          type="submit"
          // This prevents double-clicks while logging in.
          disabled={isSubmitting}
          // This styles the button and greys it out when disabled.
          className="w-full rounded-lg bg-emerald-600 py-2.5 font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {/* This changes the text while the request runs. */}
          {isSubmitting ? "Logging in..." : "Log in"}
        </button>
      </form>
    </AuthCard>
  );
}
