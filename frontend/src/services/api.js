// This imports Axios, the library we use to send HTTP requests to the Flask API.
import axios from "axios";

// This reads the API address from VITE_API_URL if set, otherwise uses the local Flask server.
export const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:5000/api";

// This is the localStorage key under which the login token is kept.
const TOKEN_KEY = "nse_paper_trader_token";

// This is the name of the browser event fired when the server rejects our token.
export const AUTH_EXPIRED_EVENT = "auth:expired";

// These helpers read, save, and remove the login token in the browser's localStorage.
export const tokenStorage = {
  // This returns the saved token, or null if the student is not logged in.
  get: () => localStorage.getItem(TOKEN_KEY),
  // This saves a new token after login.
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  // This deletes the token on logout or expiry.
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

// This creates one shared Axios client so every request uses the same base URL and timeout.
const api = axios.create({
  // Every path like "/stocks" is added to this address.
  baseURL: API_BASE_URL,
  // This gives up after 15 seconds instead of hanging forever.
  timeout: 15000,
});

// This runs before every request and attaches the login token if we have one.
api.interceptors.request.use((config) => {
  // This reads the saved token.
  const token = tokenStorage.get();
  // This adds "Authorization: Bearer <token>", the header Flask-JWT-Extended expects.
  if (token) config.headers.Authorization = `Bearer ${token}`;
  // This lets the request continue.
  return config;
});

// This runs after every response and handles a rejected token in one place.
api.interceptors.response.use(
  // Successful responses pass straight through.
  (response) => response,
  // Failed responses are inspected here.
  (error) => {
    // A 401 from login means "wrong password", not "session expired", so it is excluded.
    const isLoginOrRegister = /\/auth\/(login|register)$/.test(error.config?.url ?? "");
    // This handles a missing, invalid, or expired token on any other route.
    if (error.response?.status === 401 && !isLoginOrRegister) {
      // This removes the dead token.
      tokenStorage.clear();
      // This tells AuthContext to log the student out and show the login page.
      window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
    }
    // This still passes the error to the code that made the request.
    return Promise.reject(error);
  },
);

// This turns any Axios error into a sentence we can show the student.
export function getErrorMessage(error, fallback = "Something went wrong. Please try again.") {
  // This uses the backend's own message, e.g. "Insufficient funds: ...".
  if (error.response?.data?.message) return error.response.data.message;
  // A request with no response means the backend is down or unreachable.
  if (error.request && !error.response) return "Cannot reach the server. Is the backend running?";
  // This covers anything unexpected.
  return fallback;
}

// This exports the shared client for all other files to use.
export default api;
