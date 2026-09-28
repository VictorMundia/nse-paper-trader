// This imports StrictMode, which warns about unsafe code patterns during development.
import { StrictMode } from "react";
// This imports the function that attaches React to the page.
import { createRoot } from "react-dom/client";
// This imports the router that keeps the URL and the page in sync without full reloads.
import { BrowserRouter } from "react-router-dom";
// This imports the component that displays pop-up messages.
import { Toaster } from "react-hot-toast";
// This imports the route map.
import App from "./App";
// This imports the login state provider.
import { AuthProvider } from "./context/AuthContext";
// This imports Tailwind CSS.
import "./styles/index.css";

// This draws the app inside <div id="root"> in index.html.
createRoot(document.getElementById("root")).render(
  <StrictMode>
    {/* The router must wrap everything that uses links or navigation. */}
    <BrowserRouter>
      {/* The auth provider sits inside the router so it can be used by pages and guards. */}
      <AuthProvider>
        {/* This is the app itself. */}
        <App />
        {/* This shows pop-ups at the top centre, each for 4 seconds. */}
        <Toaster position="top-center" toastOptions={{ duration: 4000 }} />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
