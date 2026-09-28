// This imports defineConfig so the editor can autocomplete Vite settings.
import { defineConfig } from "vite";
// This imports the React plugin, which compiles JSX and enables instant reload on save.
import react from "@vitejs/plugin-react";
// This imports the Tailwind CSS v4 plugin, which generates only the utility classes we use.
import tailwindcss from "@tailwindcss/vite";

// This exports the Vite configuration.
export default defineConfig({
  // This turns on React and Tailwind support.
  plugins: [react(), tailwindcss()],
  // This configures the development server.
  server: {
    // This is the port the backend's CORS list allows.
    port: 5173,
    // Fail instead of silently moving to 5174, which CORS would block.
    strictPort: true,
  },
});
