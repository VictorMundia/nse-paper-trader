// This imports useState to hold the email and the "sent" state.
import { useState } from "react";
// This imports Link for the "back to login" link.
import { Link } from "react-router-dom";
// This imports the "email sent" icon.
import { MailCheck } from "lucide-react";
// This imports toast for error pop-ups.
import toast from "react-hot-toast";
// This imports the shared card layout.
import AuthCard from "../components/AuthCard";
// This imports the API client and error helper.
import api, { getErrorMessage } from "../services/api";

// These are the Tailwind classes for the input.
const inputClass =
  "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200";

// This page asks for an email and sends a reset link.
export default function ForgotPasswordPage() {
  // This holds the email typed so far.
  const [email, setEmail] = useState("");
  // This holds the server's confirmation once the request succeeds.
  const [sentMessage, setSentMessage] = useState(null);
  // This is true while the request is in flight.
  const [isSubmitting, setIsSubmitting] = useState(false);

  // This runs when the form is submitted.
  const handleSubmit = async (event) => {
    // This stops the browser from reloading the page.
    event.preventDefault();
    // This disables the button.
    setIsSubmitting(true);
    // This sends the request.
    try {
      // The server replies the same way whether or not the email is registered.
      const { data } = await api.post("/auth/forgot-password", { email });
      // This switches the page to the confirmation view.
      setSentMessage(data.message);
    } catch (error) {
      // This shows network or validation errors.
      toast.error(getErrorMessage(error));
    } finally {
      // This re-enables the button.
      setIsSubmitting(false);
    }
  };

  // This returns the page layout.
  return (
    <AuthCard
      // This is the card title.
      title="Forgot your password?"
      // This is the line under the title.
      subtitle="Enter your email and we will send you a link to choose a new one."
      // This is the link below the card.
      footer={
        <Link to="/login" className="font-medium text-emerald-700 hover:underline">
          Back to log in
        </Link>
      }
    >
      {sentMessage ? (
        // This is shown after submitting.
        <div className="flex gap-3 rounded-lg bg-emerald-50 p-4 text-sm text-emerald-800">
          {/* This is the "email sent" icon. */}
          <MailCheck className="h-5 w-5 shrink-0" aria-hidden="true" />
          {/* This is the server's neutral confirmation. */}
          <p>{sentMessage} Check your inbox and spam folder.</p>
        </div>
      ) : (
        // This is the email form.
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* This is the email field. */}
          <label className="block text-sm font-medium">
            Email
            <input type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} className={inputClass} />
          </label>
          {/* This is the submit button. */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-emerald-600 py-2.5 font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? "Sending..." : "Send reset link"}
          </button>
        </form>
      )}
    </AuthCard>
  );
}
