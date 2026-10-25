import { useRef, useEffect, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { sendChat, UnauthorizedError, type Source } from "../api/client";
import HistoryPanel from "../components/HistoryPanel";
import { type HistoryItem } from "../api/client";

interface Message {
  from: "user" | "bot";
  text: string;
  sources?: Source[];
  pii?: string[];
  blocked?: boolean;
}

export default function ChatPage() {
  const { token, username, role, logout } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const bottom = useRef<HTMLDivElement>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  const doLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const q = input.trim();
    if (!q || !token || busy) return;
    setInput("");
    setMessages((m) => [...m, { from: "user", text: q }]);
    setBusy(true);
    try {
      const r = await sendChat(token, q);
      setMessages((m) => [
        ...m,
        { from: "bot", text: r.answer, sources: r.sources, pii: r.pii_found, blocked: r.blocked },
      ]);
      setRefreshKey((k) => k + 1);   // moved here: the server has saved it by now
    } catch (err) {
      if (err instanceof UnauthorizedError) {
        doLogout();
        return;
      }
      const msg = err instanceof TypeError ? "Cannot reach the API." : (err as Error).message;
      setMessages((m) => [...m, { from: "bot", text: msg }]);
    } finally {
      setBusy(false);
    }
  };

  const openHistory = (it: HistoryItem) => {
    setMessages((m) => [
      ...m,
      { from: "user", text: it.query },
      { from: "bot", text: it.answer, sources: it.sources },
    ]);
  };

  return (
    <div className="layout">
      {token && <HistoryPanel token={token} refreshKey={refreshKey} onOpen={openHistory} />}
      <div className="chat">
        <div className="chat">
          <header>
            <strong>🔒 Secure RAG</strong>
            <span>
              {username} <span className="badge">{role}</span>
              <button className="link" onClick={doLogout}>Log out</button>
            </span>
          </header>

          <main>
            {messages.length === 0 && <p className="hint">Ask a question about company documents.</p>}
            {messages.map((m, i) => (
              <div key={i} className={`bubble ${m.from}`}>
                <p>{m.text}</p>
                {m.pii && m.pii.length > 0 && (
                  <p className="notice info">Sensitive data masked before processing: {m.pii.join(", ")}</p>
                )}
                {m.blocked && <p className="notice warn">Blocked by the security guardrails.</p>}
                {m.sources && m.sources.length > 0 && (
                  <details>
                    <summary>Sources ({m.sources.length})</summary>
                    <ul>
                      {m.sources.map((s, j) => (
                        <li key={j}>{s.source} (page {s.page})</li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>
            ))}
            {busy && <div className="bubble bot"><p>Thinking...</p></div>}
            <div ref={bottom} />
          </main>

          <form className="composer" onSubmit={submit}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about company documents"
            />
            <button disabled={busy || !input.trim()}>Send</button>
          </form>
        </div>
      </div>
    </div>
  );
}