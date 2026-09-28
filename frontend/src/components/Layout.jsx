// This imports Outlet, which shows whichever child page matches the URL.
import { Outlet } from "react-router-dom";
// This imports the top navigation bar.
import Navbar from "./Navbar";

// This is the frame around every logged-in page: navbar on top, page content below.
export default function Layout() {
  // This returns the page frame.
  return (
    // This makes the frame at least as tall as the screen.
    <div className="min-h-screen">
      {/* This is the navigation bar. */}
      <Navbar />
      {/* This is the page area, centred with a maximum width. */}
      <main className="mx-auto max-w-6xl px-4 py-8">
        {/* This is where the current page is drawn. */}
        <Outlet />
      </main>
    </div>
  );
}
