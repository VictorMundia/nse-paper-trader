// This imports router tools: Navigate redirects and Outlet shows the child page.
import { Navigate, Outlet } from "react-router-dom";
// This imports the login state.
import { useAuth } from "../context/AuthContext";
// This imports the loading spinner.
import FullPageSpinner from "./FullPageSpinner";

// This guard keeps logged-in students away from the login and register pages.
export default function PublicOnlyRoute() {
  // This reads who is logged in and whether we are still checking.
  const { user, isLoading } = useAuth();
  // This waits for the saved-token check.
  if (isLoading) return <FullPageSpinner />;
  // A logged-in student has no reason to see /login, so they go to the dashboard.
  if (user) return <Navigate to="/" replace />;
  // This shows the login or register page.
  return <Outlet />;
}
