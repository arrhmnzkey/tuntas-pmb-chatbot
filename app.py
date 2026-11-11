import os
import uuid

from flask import Flask, jsonify, render_template, request, session

from chatbot.database import ChatHistory
from chatbot.engine import ChatbotEngine, load_theme

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "ganti-di-produksi"),
        THRESHOLD=float(os.environ.get("THRESHOLD", "0.45")),
        DATABASE=os.environ.get("DATABASE", os.path.join(BASE_DIR, "chat_history.db")),
        ADMIN_KEY=os.environ.get("ADMIN_KEY", ""),
        THEME_FILE=os.path.join(BASE_DIR, "themes", "pmb.json"),
    )
    if config:
        app.config.update(config)

    theme = load_theme(app.config["THEME_FILE"])
    bot = ChatbotEngine(theme, threshold=app.config["THRESHOLD"])
    history = ChatHistory(app.config["DATABASE"])

    def get_session_id():
        if "sid" not in session:
            session["sid"] = uuid.uuid4().hex
        return session["sid"]

    def galat(pesan, kode=400):
        return jsonify({"error": pesan}), kode

    # ---------- halaman HTML ----------
    @app.get("/")
    def landing():
        return render_template("landing.html", theme=theme)

    @app.get("/chat")
    def chat():
        return render_template("chat.html", theme=theme)

    @app.get("/admin")
    def admin():
        kunci = app.config["ADMIN_KEY"]
        if kunci and request.args.get("key") != kunci:
            return "Kunci admin salah", 403
        return render_template("admin.html", theme=theme, s=history.stats(),
                               threshold=app.config["THRESHOLD"])

    # ---------- REST API ----------
    @app.post("/api/chat")
    def api_chat():
        data = request.get_json(silent=True)
        if data is None:
            return galat("Body harus berformat JSON")
        message = str(data.get("message", "")).strip()
        if not message:
            return galat("Pesan tidak boleh kosong")
        if len(message) > 500:
            return galat("Pesan maksimal 500 karakter")

        sid = get_session_id()
        hasil = bot.reply(message)
        history.add(sid, "user", message, hasil["intent"], hasil["score"])
        history.add(sid, "bot", hasil["reply"], hasil["intent"], hasil["score"])
        if data.get("debug"):
            hasil["candidates"] = bot.candidates(message)
        return jsonify(hasil)

    @app.get("/api/history")
    def api_history():
        return jsonify(history.get(get_session_id()))

    @app.delete("/api/history")
    def api_history_clear():
        history.clear(get_session_id())
        return jsonify({"ok": True})

    @app.get("/api/stats")
    def api_stats():
        kunci = app.config["ADMIN_KEY"]
        if kunci and request.args.get("key") != kunci:
            return galat("Kunci admin salah", 403)
        return jsonify(history.stats())

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
