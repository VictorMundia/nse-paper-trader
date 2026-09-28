// This imports the React tools for shared state (context), memoised functions, and side effects.
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
// This imports toast so we can show pop-up messages.
import toast from "react-hot-toast";
// This imports the shared API client, the expiry event name, and the token helpers.
import api, { AUTH_EXPIRED_EVENT, tokenStorage } from "../services/api";

// This creates the context object that holds login state for the whole app.
const AuthContext = createContext(null);

// This component wraps the app and provides the login state to every page.
export function AuthProvider({ children }) {
  // This holds the logged-in student's profile, or null when logged out.
  const [user, setUser] = useState(null);
  // This is true while we check a saved token on first load, so pages do not flash the login screen.
  const [isLoading, setIsLoading] = useState(true);

  // This loads the student's current profile (name, balance, level) from /auth/me.
  const refreshUser = useCallback(async () => {
    // This asks the backend who the token belongs to.
    const { data } = await api.get("/auth/me");
    // This stores the profile.
    setUser(data);
    // This returns it so callers can use it straight away.
    return data;
  }, []);

  // This runs once on page load: if a token was saved earlier, it restores the session.
  useEffect(() => {
    // With no saved token there is nothing to check.
    if (!tokenStorage.get()) {
      // This ends the loading state immediately.
      setIsLoading(false);
      // This stops the effect here.
      return;
    }
    // This checks the saved token with the backend.
    refreshUser()
      // A rejected token is removed so the student sees the login page.
      .catch(() => {
        // This deletes the bad token.
        tokenStorage.clear();
        // This marks the student as logged out.
        setUser(null);
      })
      // This ends the loading state either way.
      .finally(() => setIsLoading(false));
  }, [refreshUser]);

  // This listens for the "token rejected" event fired by the API client.
  useEffect(() => {
    // This logs the student out and explains why.
    const handleExpired = () => {
      // This clears the profile, which makes ProtectedRoute redirect to /login.
      setUser(null);
      // The fixed id stops several failed requests from showing several identical pop-ups.
      toast.error("Your session has ended. Please log in again.", { id: "session-expired" });
    };
    // This starts listening.
    window.addEventListener(AUTH_EXPIRED_EVENT, handleExpired);
    // This stops listening if the provider is ever removed.
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, handleExpired);
  }, []);

  // This logs in, saves the token, and loads the profile.
  const login = useCallback(
    async (email, password) => {
      // This sends the credentials to the backend.
      const { data } = await api.post("/auth/login", { email, password });
      // This saves the token so it survives a page refresh.
      tokenStorage.set(data.access_token);
      // This loads and returns the full profile.
      return refreshUser();
    },
    [refreshUser],
  );

  // This creates an account and then logs straight in.
  const register = useCallback(
    async (fields) => {
      // This creates the account; the backend validates every field.
      await api.post("/auth/register", fields);
      // This logs in with the same email and password.
      return login(fields.email, fields.password);
    },
    [login],
  );

  // This logs out by forgetting the token and the profile.
  const logout = useCallback(() => {
    // This deletes the saved token.
    tokenStorage.clear();
    // This clears the profile, which sends the student to /login.
    setUser(null);
  }, []);

  // useMemo keeps the same object between renders so pages only re-render when login state changes.
  const value = useMemo(
    () => ({ user, isLoading, login, register, logout, refreshUser }),
    [user, isLoading, login, register, logout, refreshUser],
  );

  // This makes the login state available to everything inside the provider.
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// This hook lets any component read the login state with one line: const { user } = useAuth();
export function useAuth() {
  // This reads the nearest AuthContext value.
  const context = useContext(AuthContext);
  // This catches the mistake of using the hook outside <AuthProvider>.
  if (!context) throw new Error("useAuth must be used inside <AuthProvider>.");
  // This returns the login state and actions.
  return context;
}
