import { useEffect, useState } from "react";
import { getHistory, deleteHistoryItem, clearHistory, type HistoryItem } from "../api/client";

interface Props {
  token: string;
  refreshKey: number;
  onOpen: (item: HistoryItem) => void;
}

export default function HistoryPanel({ token, refreshKey, onOpen }: Props) {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [q, setQ] = useState("");

  const load = () => getHistory(token, q).then(setItems).catch(() => setItems([]));

  // debounce typing, and reload after each new answer
  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, refreshKey]);

  const remove = async (id: number) => {
    await deleteHistoryItem(token, id);
    load();
  };

  const clearAll = async () => {
    if (!window.confirm("Delete all your history?")) return;
    await clearHistory(token);
    load();
  };

  return (
    <aside className="history">
      <h3>History</h3>
      <input placeholder="Search past questions" value={q} onChange={(e) => setQ(e.target.value)} />
      <ul>
        {items.map((it) => (
          <li key={it.id}>
            <button className="hist-q" onClick={() => onOpen(it)} title={it.query}>
              {it.query}
            </button>
            <button className="hist-x" onClick={() => remove(it.id)} aria-label="Delete">×</button>
          </li>
        ))}
      </ul>
      {items.length === 0 && <p className="hint">{q ? "No matches." : "No saved questions yet."}</p>}
      {items.length > 0 && !q && <button className="link" onClick={clearAll}>Clear all</button>}
    </aside>
  );
}