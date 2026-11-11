"""Coba chatbot di terminal: python cli.py [--debug]"""
import argparse
import os

from chatbot.engine import ChatbotEngine, load_theme

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", help="tampilkan 3 kandidat teratas")
args = parser.parse_args()

theme = load_theme(os.path.join(os.path.dirname(__file__), "themes", "pmb.json"))
bot = ChatbotEngine(theme)

print(theme["greeting"])
print("\n(ketik 'keluar' untuk berhenti)")
while True:
    pesan = input("\nAnda: ").strip()
    if pesan.lower() == "keluar":
        break
    if not pesan:
        continue
    hasil = bot.reply(pesan)
    print("Bot :", hasil["reply"])
    print(f"      [intent: {hasil['intent']} · skor {hasil['score']:.2f}]")
    if args.debug:
        for c in bot.candidates(pesan):
            print(f"      - {c['intent']:<22}{c['score']:.2f}  pola: \"{c['pattern']}\"")
