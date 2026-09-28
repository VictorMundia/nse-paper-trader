// This imports router tools: Navigate redirects, Outlet shows the child page, useLocation reads the current URL.
import { Navigate, Outlet, useLocation } from "react-router-dom";
// This imports the login state.
import { useAuth } from "../context/AuthContext";
// This imports the loading spinner.
import FullPageSpinner from "./FullPageSpinner";

// This guard only lets logged-in students see the pages inside it.
export default function ProtectedRoute() {
  // This reads who is logged in and whether we are still checking.
  const { user, isLoading } = useAuth();
  // This reads the page the student was trying to open.
  const location = useLocation();
  // This waits for the saved-token check so a refresh does not bounce the student to /login.
  if (isLoading) return <FullPageSpinner label="Checking your session..." />;
  // This sends logged-out visitors to /login, remembering where they wanted to go.
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  // This shows the requested page.
  return <Outlet />;
}
