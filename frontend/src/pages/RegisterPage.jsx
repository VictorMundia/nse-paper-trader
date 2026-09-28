// This imports useState to hold what the student types.
import { useState } from "react";
// This imports Link for the login link and useNavigate to redirect after registering.
import { Link, useNavigate } from "react-router-dom";
// This imports toast for success and error pop-ups.
import toast from "react-hot-toast";
// This imports the shared card layout.
import AuthCard from "../components/AuthCard";
// This imports the register action.
import { useAuth } from "../context/AuthContext";
// This imports the helper that turns API errors into readable text.
import { getErrorMessage } from "../services/api";

// These are the Tailwind classes shared by every input.
const inputClass =
  "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200";

// These match EXPERIENCE_LEVELS in backend/app/routes/auth.py; the server is the real check.
const EXPERIENCE_OPTIONS = [
  // For students who have never bought shares.
  { value: "beginner", label: "Beginner — I have never invested" },
  // For students who have tried investing a little.
  { value: "intermediate", label: "Intermediate — I have invested a little" },
  // For students who invest regularly.
  { value: "advanced", label: "Advanced — I invest regularly" },
];

// This is the registration page.
export default function RegisterPage() {
  // This holds every field in one object so one change handler can update any of them.
  const [form, setForm] = useState({ full_name: "", email: "", password: "", experience_level: "" });
  // This is true while the request is in flight, to stop double submission.
  const [isSubmitting, setIsSubmitting] = useState(false);
  // This reads the register action.
  const { register } = useAuth();
  // This lets us redirect after registering.
  const navigate = useNavigate();

  // This updates whichever field changed, using the input's name attribute.
  const handleChange = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  // This runs when the form is submitted.
  const handleSubmit = async (event) => {
    // This stops the browser from reloading the page.
    event.preventDefault();
    // This disables the button.
    setIsSubmitting(true);
    // This attempts the registration.
    try {
      // This creates the account and logs in.
      const user = await register(form);
      // This confirms the new account and the starting balance.
      toast.success(`Welcome, ${user.full_name.split(" ")[0]}! You have KES 100,000 to invest.`);
      // This opens the dashboard.
      navigate("/", { replace: true });
    } catch (error) {
      // This shows the backend's message, e.g. "Email is already registered."
      toast.error(getErrorMessage(error));
      // This re-enables the button.
      setIsSubmitting(false);
    }
  };

  // This returns the page layout.
  return (
    // This wraps the form in the shared card.
    <AuthCard
      // This is the card title.
      title="Create your account"
      // This is the line under the title.
      subtitle="Start with KES 100,000 in virtual money. No real money is ever used."
      // This is the link below the card.
      footer={
        <>
          Already registered?{" "}
          <Link to="/login" className="font-medium text-emerald-700 hover:underline">
            Log in
          </Link>
        </>
      }
    >
      {/* This is the registration form. */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* This is the full name field. */}
        <label className="block text-sm font-medium">
          Full name
          {/* minLength and maxLength match the backend rules (2-120 characters). */}
          <input name="full_name" autoComplete="name" required minLength={2} maxLength={120} value={form.full_name} onChange={handleChange} className={inputClass} />
        </label>
        {/* This is the email field. */}
        <label className="block text-sm font-medium">
          Email
          {/* type="email" gives phones the @ keyboard and basic format checking. */}
          <input name="email" type="email" autoComplete="email" required maxLength={120} value={form.email} onChange={handleChange} className={inputClass} />
        </label>
        {/* This is the password field. */}
        <label className="block text-sm font-medium">
          Password
          {/* minLength matches the backend's 8-character minimum. */}
          <input name="password" type="password" autoComplete="new-password" required minLength={8} value={form.password} onChange={handleChange} className={inputClass} />
          {/* This tells the student the rule before they get it wrong. */}
          <span className="mt-1 block text-xs font-normal text-slate-500">At least 8 characters.</span>
        </label>
        {/* This is the experience level dropdown, used to group participants in the study. */}
        <label className="block text-sm font-medium">
          Investing experience
          <select name="experience_level" required value={form.experience_level} onChange={handleChange} className={inputClass}>
            {/* The empty first option forces a real choice; required blocks submitting it. */}
            <option value="" disabled>
              Choose one...
            </option>
            {/* This draws one option per level. */}
            {EXPERIENCE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        {/* This is the submit button. */}
        <button
          // This submits the form.
          type="submit"
          // This prevents double-clicks while registering.
          disabled={isSubmitting}
          // This styles the button and greys it out when disabled.
          className="w-full rounded-lg bg-emerald-600 py-2.5 font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {/* This changes the text while the request runs. */}
          {isSubmitting ? "Creating account..." : "Create account"}
        </button>
      </form>
    </AuthCard>
  );
}
