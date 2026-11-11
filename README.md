# TUNTAS PMB — Chatbot Tematik Rule-Based (Flask)

Chatbot tematik berbasis aturan (rule-based) untuk informasi Penerimaan Mahasiswa Baru, dibuat dengan Flask. Tanpa LLM, RAG, maupun API eksternal.

## Fitur
- Halaman landing, halaman chat, dan halaman admin statistik
- Pencocokan pola dengan skor kemiripan (Jaccard + Fuzzy + Cakupan), ambang 0,45
- Normalisasi kata tidak baku dan penghapusan stopword
- Riwayat percakapan tersimpan di SQLite
- REST API dan uji otomatis dengan pytest

## Menjalankan
```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

python cli.py --debug          # coba di terminal
python app.py                  # web: http://127.0.0.1:5000
pytest -v                      # uji otomatis
python evaluate.py --sweep     # akurasi per ambang
```
Halaman admin: http://127.0.0.1:5000/admin

## Struktur

| File | Fungsi |
|---|---|
| themes/pmb.json | Seluruh pengetahuan bot (intent, pola, respons, fallback) |
| chatbot/engine.py | Praproses, skor kemiripan, ambang 0,45, jawaban |
| chatbot/database.py | Riwayat dan statistik SQLite |
| app.py | Route halaman + REST API |
| templates/, static/ | Tampilan (HTML, CSS, chat.js dengan fetch) |
| tests/ | Uji unit dan integrasi |
| evaluasi/pmb.csv | Data uji untuk akurasi |

## Skor kemiripan

skor = 0,4 × Jaccard + 0,3 × Fuzzy + 0,3 × Cakupan; jawab bila skor ≥ 0,45, selain itu fallback.