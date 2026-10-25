import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(username, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof TypeError ? "Cannot reach the API. Is uvicorn running?" : (err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card login">
      <h1>🔒 Secure RAG</h1>
      <form onSubmit={submit}>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error && <p className="error">{error}</p>}
        <button disabled={busy || !username || !password}>{busy ? "Logging in..." : "Log in"}</button>
      </form>
      <p className="hint">Demo users: alice (employee), harry (hr), frank (finance), root (admin)</p>
    </div>
  );
}