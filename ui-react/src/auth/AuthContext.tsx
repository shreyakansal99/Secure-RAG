import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { getMe, login as apiLogin } from "../api/client";

interface AuthState {
  token: string | null;
  username: string | null;
  role: string | null;
  ready: boolean;
  login: (u: string, p: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);
const KEY = "secure-rag-token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(sessionStorage.getItem(KEY));
  const [username, setUsername] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  const logout = () => {
    sessionStorage.removeItem(KEY);
    setToken(null);
    setUsername(null);
    setRole(null);
  };

  // On load or refresh, confirm the stored token is still valid
  useEffect(() => {
    if (!token) {
      setReady(true);
      return;
    }
    getMe(token)
      .then((me) => {
        setUsername(me.username);
        setRole(me.role);
      })
      .catch(() => logout())
      .finally(() => setReady(true));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (u: string, p: string) => {
    const t = await apiLogin(u, p);
    const me = await getMe(t);
    sessionStorage.setItem(KEY, t);
    setToken(t);
    setUsername(me.username);
    setRole(me.role);
  };

  return (
    <AuthContext.Provider value={{ token, username, role, ready, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}