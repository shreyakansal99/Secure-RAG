const API = "http://127.0.0.1:8000";

export class UnauthorizedError extends Error {}

export interface Source {
  source: string;
  page: number;
}

export interface ChatResponse {
  user: string;
  role: string;
  answer: string;
  sources: Source[];
  pii_found: string[];
  blocked: boolean;
  block_reason: string | null;
  output_flags: string[];
}

export interface Me {
  username: string;
  role: string;
}

export interface HistoryItem {
  id: number;
  ts: string;
  query: string;
  answer: string;
  sources: Source[];
}

async function authed(token: string, path: string, method = "GET") {
  const r = await fetch(`${API}${path}`, {
    method,
    headers: { Authorization: `Bearer ${token}` },
  });
  if (r.status === 401) throw new UnauthorizedError();
  if (!r.ok) throw new Error(`Server error (${r.status})`);
  return r.json();
}

export const getHistory = (token: string, q = ""): Promise<HistoryItem[]> =>
  authed(token, `/history?q=${encodeURIComponent(q)}`);
export const deleteHistoryItem = (token: string, id: number) =>
  authed(token, `/history/${id}`, "DELETE");
export const clearHistory = (token: string) => authed(token, "/history", "DELETE");

export async function login(username: string, password: string): Promise<string> {
  // /login expects form data, not JSON
  const body = new URLSearchParams({ username, password });
  const r = await fetch(`${API}/login`, { method: "POST", body });
  if (!r.ok) throw new Error("Wrong username or password");
  const data = await r.json();
  return data.access_token as string;
}

export async function getMe(token: string): Promise<Me> {
  const r = await fetch(`${API}/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (r.status === 401) throw new UnauthorizedError();
  if (!r.ok) throw new Error(`Server error (${r.status})`);
  return r.json();
}

export async function sendChat(token: string, query: string): Promise<ChatResponse> {
  const r = await fetch(`${API}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ query }),
  });
  if (r.status === 401) throw new UnauthorizedError();
  if (!r.ok) throw new Error(`Server error (${r.status})`);
  return r.json();
}