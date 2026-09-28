// This imports the router components that match URLs to pages.
import { Route, Routes } from "react-router-dom";
// This imports the frame (navbar + content) for logged-in pages.
import Layout from "./components/Layout";
// This imports the account page with change password.
import AccountPage from "./pages/AccountPage";
// This imports the "forgot password" page.
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
// This imports the page opened from the reset email.
import ResetPasswordPage from "./pages/ResetPasswordPage";
// This imports the "coming soon" page used for sections later phases build.
import PlaceholderPage from "./components/PlaceholderPage";
// This imports the guard that requires login.
import ProtectedRoute from "./components/ProtectedRoute";
// This imports the guard that hides login/register from logged-in students.
import PublicOnlyRoute from "./components/PublicOnlyRoute";
// This imports the dashboard page.
import DashboardPage from "./pages/DashboardPage";
// This imports the login page.
import LoginPage from "./pages/LoginPage";
// This imports the 404 page.
import NotFoundPage from "./pages/NotFoundPage";
// This imports the registration page.
import RegisterPage from "./pages/RegisterPage";

// This is the map of every URL in the app.
export default function App() {
  // This returns the routes.
  return (
    <Routes>
      {/* These pages are only for logged-out visitors. */}
      <Route element={<PublicOnlyRoute />}>
        {/* The login page. */}
        <Route path="/login" element={<LoginPage />} />
        {/* The registration page. */}
        <Route path="/register" element={<RegisterPage />} />
        {/* The "forgot password" page. */}
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      </Route>
      {/* The reset page is outside both guards so the email link works whether or not someone is logged in. */}
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      {/* These pages require login and share the navbar layout. */}
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          {/* "index" means this is the page for "/" itself. */}
          <Route index element={<DashboardPage />} />
          {/* The stock explorer, built in Phase 8. */}
          <Route path="/stocks" element={<PlaceholderPage title="Stocks" description="Browse the 15 NSE stocks, view price charts, and buy or sell shares." phase={8} />} />
          {/* The portfolio page, built in Phase 7. */}
          <Route path="/portfolio" element={<PlaceholderPage title="Portfolio" description="Your holdings, their current value, and your profit or loss." phase={7} />} />
          {/* The trade history page, built in Phase 7. */}
          <Route path="/history" element={<PlaceholderPage title="Trade history" description="Every buy and sell you have made, newest first." phase={7} />} />
          {/* The account page with change password. */}
          <Route path="/account" element={<AccountPage />} />
        </Route>
      </Route>
      {/* "*" matches any address not listed above. */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
