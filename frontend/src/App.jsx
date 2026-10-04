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
// This imports the guard that requires login.
import ProtectedRoute from "./components/ProtectedRoute";
// This imports the guard that hides login/register from logged-in students.
import PublicOnlyRoute from "./components/PublicOnlyRoute";
// This imports the dashboard page.
import DashboardPage from "./pages/DashboardPage";
// This imports the leaderboard page.
import LeaderboardPage from "./pages/LeaderboardPage";
// This imports the lessons page.
import LearnPage from "./pages/LearnPage";
// This imports the login page.
import LoginPage from "./pages/LoginPage";
// This imports the 404 page.
import NotFoundPage from "./pages/NotFoundPage";
// This imports the portfolio page.
import PortfolioPage from "./pages/PortfolioPage";
// This imports the registration page.
import RegisterPage from "./pages/RegisterPage";
// This imports the single-stock page with the trade panel.
import StockDetailPage from "./pages/StockDetailPage";
// This imports the list of all stocks.
import StocksPage from "./pages/StocksPage";
// This imports the trade history page.
import TradeHistoryPage from "./pages/TradeHistoryPage";

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
          {/* The list of all stocks. */}
          <Route path="/stocks" element={<StocksPage />} />
          {/* ":ticker" is a URL parameter, e.g. /stocks/SCOM. */}
          <Route path="/stocks/:ticker" element={<StockDetailPage />} />
          {/* The portfolio page. */}
          <Route path="/portfolio" element={<PortfolioPage />} />
          {/* The trade history page. */}
          <Route path="/history" element={<TradeHistoryPage />} />
          {/* The leaderboard. */}
          <Route path="/leaderboard" element={<LeaderboardPage />} />
          {/* The lessons, quiz, and glossary. */}
          <Route path="/learn" element={<LearnPage />} />
          {/* The account page with change password. */}
          <Route path="/account" element={<AccountPage />} />
        </Route>
      </Route>
      {/* "*" matches any address not listed above. */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
