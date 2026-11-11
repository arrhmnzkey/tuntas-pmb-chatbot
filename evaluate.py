"""Ukur akurasi: python evaluate.py [--sweep]"""
import argparse
import csv
import os

from chatbot.engine import ChatbotEngine, load_theme

BASE = os.path.dirname(os.path.abspath(__file__))
theme = load_theme(os.path.join(BASE, "themes", "pmb.json"))

with open(os.path.join(BASE, "evaluasi", "pmb.csv"), encoding="utf-8") as f:
    data = list(csv.DictReader(f))


def akurasi(threshold, tampilkan_salah=False):
    bot = ChatbotEngine(theme, threshold=threshold)
    benar = 0
    for row in data:
        tag, skor = bot.classify(row["kalimat"])
        tebakan = tag or "fallback"
        if tebakan == row["intent"]:
            benar += 1
        elif tampilkan_salah:
            print(f"  SALAH: {row['kalimat']!r} -> {tebakan} ({skor:.2f}), seharusnya {row['intent']}")
    return 100 * benar / len(data), benar


parser = argparse.ArgumentParser()
parser.add_argument("--sweep", action="store_true", help="bandingkan beberapa ambang")
args = parser.parse_args()

if args.sweep:
    print("ambang  akurasi")
    for t in (0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70):
        print(f"{t:.2f}    {akurasi(t)[0]:.1f}%")
else:
    persen, benar = akurasi(0.45, tampilkan_salah=True)
    print(f"Akurasi: {benar}/{len(data)} = {persen:.1f}%")
