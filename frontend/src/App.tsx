import { useState } from "react";

type Msg = { role: "user" | "assistant"; text: string };

export default function App() {
  const [input, setInput]   = useState("");
  const [log,   setLog]     = useState<Msg[]>([]);        // chat history
  const [busy,  setBusy]    = useState(false);

  async function downloadState() {
    try {
      const response = await fetch("http://localhost:8000/state");
      const data = await response.json();
      const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
        JSON.stringify(data, null, 2)
      )}`;
      const link = document.createElement("a");
      link.href = jsonString;
      link.download = "game_params.json";
      link.click();
    } catch (err) {
      console.error("Failed to download game state:", err);
      // Optionally, display an error message to the user
      setLog(l => [...l, { role: "assistant", text: `Failed to download state: ${err}` }]);
    }
  }

  async function send() {
    if (!input.trim() || busy) return;
    const userMsg: Msg = { role: "user", text: input };
    setLog(l => [...l, userMsg]);
    setInput("");
    setBusy(true);

    try {
      const r = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.text })
      });
      const data = await r.json();
      const botMsg: Msg = { role: "assistant", text: data.response };
      setLog(l => [...l, botMsg]);
    } catch (err) {
      setLog(l => [...l, { role: "assistant", text: String(err) }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center bg-gray-50 py-6 relative">
      <button
        onClick={downloadState}
        className="absolute top-4 right-4 text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded opacity-50 hover:opacity-100"
        title="Download game parameters"
      >
        Download game params
      </button>

      <div className="w-full max-w-xl flex flex-col gap-4">
        <h1 className="text-2xl font-semibold text-center">🎮 Game-Config Chat</h1>

        {/* chat window */}
        <div className="flex-1 border rounded-xl p-4 h-[60vh] overflow-y-auto bg-white shadow">
          {log.map((m, i) => (
            <p key={i} className={m.role === "user" ? "text-right" : "text-left"}>
              <span className={m.role === "user" ? "font-medium text-blue-600" : "text-green-700"}>
                {m.role === "user" ? "You" : "Bot"}:
              </span>{" "}
              {m.text}
            </p>
          ))}
          {busy && <p className="italic text-gray-400">…thinking</p>}
        </div>

        {/* input */}
        <div className="flex gap-2">
          <input
            className="flex-1 border rounded-xl px-3 py-2 shadow-sm"
            placeholder="Type your message…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && send()}
            disabled={busy}
          />
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded-xl shadow disabled:opacity-40"
            onClick={send}
            disabled={busy}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
} 