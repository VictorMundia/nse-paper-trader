// This imports Link to send the student back home.
import { Link } from "react-router-dom";

// This page is shown for any address that does not match a route.
export default function NotFoundPage() {
  // This returns the page layout.
  return (
    // This centres the message on the screen.
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
      {/* This is the large 404 code. */}
      <p className="text-6xl font-bold text-emerald-600">404</p>
      {/* This explains the problem. */}
      <h1 className="text-xl font-semibold">Page not found</h1>
      {/* This offers a way out; logged-out visitors are sent on to /login by ProtectedRoute. */}
      <Link to="/" className="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700">
        Go to dashboard
      </Link>
    </div>
  );
}
