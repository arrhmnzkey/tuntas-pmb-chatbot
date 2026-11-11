const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const box = document.getElementById("messages");

function addMessage(who, text, meta) {
  const wrap = document.createElement("div");
  wrap.className = "msg msg-" + who;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text; // textContent: aman dari XSS
  wrap.appendChild(bubble);
  if (meta) {
    const m = document.createElement("div");
    m.className = "meta";
    m.textContent = meta;
    wrap.appendChild(m);
  }
  box.appendChild(wrap);
  box.scrollTop = box.scrollHeight;
}

async function sendMessage(text) {
  addMessage("user", text);
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: text}),
    });
    const data = await res.json();
    if (!res.ok) return addMessage("bot", data.error);
    const meta = "intent: " + (data.intent || "tidak dikenali") +
                 " · skor " + data.score.toFixed(2);
    addMessage("bot", data.reply, meta);
  } catch (err) {
    addMessage("bot", "Gagal terhubung ke server.");
  }
}

async function loadHistory() {
  try {
    const res = await fetch("/api/history");
    const rows = await res.json();
    if (rows.length === 0) return addMessage("bot", GREETING);
    rows.forEach(r => addMessage(r.sender, r.text));
  } catch (err) {
    addMessage("bot", GREETING);
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault(); // jangan muat ulang halaman
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendMessage(text);
});

document.querySelectorAll(".chip").forEach(btn =>
  btn.addEventListener("click", () => sendMessage(btn.textContent)));

document.getElementById("clear-btn").addEventListener("click", async () => {
  await fetch("/api/history", {method: "DELETE"});
  box.textContent = "";
  addMessage("bot", GREETING);
});

loadHistory();
