import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const { token, ready } = useAuth();
  if (!ready) return <p className="center">Loading...</p>;
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}