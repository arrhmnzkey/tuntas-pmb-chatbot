"""Mesin chatbot rule-based: praproses -> skor kemiripan -> ambang -> jawaban.

Tidak mengimpor Flask, sehingga mudah diuji dan bisa dipakai di terminal.
"""
import json
import random
import re
from difflib import SequenceMatcher

THRESHOLD = 0.45

# Kata tidak baku / berimbuhan -> bentuk baku
NORMALISASI = {
    "gmn": "bagaimana", "gimana": "bagaimana", "brp": "berapa",
    "kpn": "kapan", "yg": "yang", "dgn": "dengan", "utk": "untuk",
    "gak": "tidak", "ga": "tidak", "tdk": "tidak", "udh": "sudah",
    "daftar2": "daftar", "dftr": "daftar", "jurusannya": "jurusan",
    "pendaftaran": "daftar", "daftarnya": "daftar", "mendaftar": "daftar", "pembayaran": "bayar",
    "dibayar": "bayar", "persyaratan": "syarat", "masuknya": "masuk",
    "dibuka": "buka", "ditutup": "tutup", "diupload": "upload",
    "diunggah": "upload", "unggah": "upload", "biayanya": "biaya",
    "kuliahnya": "kuliah", "prodinya": "prodi", "beasiswanya": "beasiswa",
    "sks": "sks", "perkuliahan": "kuliah",
}

STOPWORDS = {
    "yang", "di", "ke", "dari", "apa", "apakah", "saja", "aja", "nih", "dong",
    "ya", "kak", "min", "admin", "tolong", "mau", "ada", "bisa", "lewat",
    "dengan", "untuk", "itu", "ini", "dan", "atau", "info", "informasi",
    "saya", "aku", "kah", "sih", "deh", "per", "pada", "harus", "tentang",
}


def preprocess(teks):
    """Huruf kecil -> buang tanda baca -> normalisasi -> buang stopword."""
    teks = re.sub(r"[^a-z0-9\s]", " ", str(teks).lower())
    tokens = []
    for kata in teks.split():
        for k in NORMALISASI.get(kata, kata).split():
            if k and k not in STOPWORDS:
                tokens.append(k)
    return tokens


def similarity(tokens_a, tokens_b):
    """skor = 0,4 Jaccard + 0,3 Fuzzy + 0,3 Cakupan (pola)."""
    a, b = set(tokens_a), set(tokens_b)
    if not a or not b:
        return 0.0
    jaccard = len(a & b) / len(a | b)
    fuzzy = SequenceMatcher(None, " ".join(tokens_a), " ".join(tokens_b)).ratio()
    cakupan = len(a & b) / len(b)
    return 0.4 * jaccard + 0.3 * fuzzy + 0.3 * cakupan


def validate_theme(theme):
    """Kembalikan daftar kesalahan struktur file tema (kosong = valid)."""
    galat = []
    for kunci in ("id", "bot_name", "fallback", "intents"):
        if kunci not in theme:
            galat.append(f"Kunci '{kunci}' tidak ada")
    for i in theme.get("intents", []):
        tag = i.get("tag", "?")
        if not i.get("patterns"):
            galat.append(f"Intent '{tag}' tidak punya pola")
        if not i.get("responses"):
            galat.append(f"Intent '{tag}' tidak punya respons")
    return galat


def load_theme(path):
    with open(path, encoding="utf-8") as f:
        theme = json.load(f)
    galat = validate_theme(theme)
    if galat:
        raise ValueError("; ".join(galat))
    return theme


class ChatbotEngine:
    def __init__(self, theme, threshold=THRESHOLD):
        self.theme = theme
        self.threshold = threshold
        self._responses = {i["tag"]: i["responses"] for i in theme["intents"]}
        # [(tag, pola_asli, token_pola)]
        self._patterns = [
            (i["tag"], p, preprocess(p))
            for i in theme["intents"] for p in i["patterns"]
        ]

    def candidates(self, pesan, n=3):
        """Skor tertinggi per intent, diurutkan (untuk debug / mode belajar)."""
        tokens = preprocess(pesan)
        terbaik = {}
        for tag, pola, tp in self._patterns:
            skor = similarity(tokens, tp)
            if tag not in terbaik or skor > terbaik[tag][0]:
                terbaik[tag] = (skor, pola)
        urut = sorted(terbaik.items(), key=lambda x: x[1][0], reverse=True)
        return [{"intent": t, "score": round(s, 2), "pattern": p}
                for t, (s, p) in urut[:n]]

    def classify(self, pesan):
        """Return (tag atau None, skor tertinggi)."""
        top = self.candidates(pesan, n=1)
        if not top:
            return None, 0.0
        skor = top[0]["score"]
        if skor < self.threshold:
            return None, skor
        return top[0]["intent"], skor

    def reply(self, pesan):
        tag, skor = self.classify(pesan)
        if tag is None:
            teks = random.choice(self.theme["fallback"])
        else:
            teks = random.choice(self._responses[tag])
        return {"reply": teks, "intent": tag, "score": skor}
