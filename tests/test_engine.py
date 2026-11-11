import os

import pytest

from chatbot.engine import ChatbotEngine, load_theme, preprocess, similarity, validate_theme

TEMA = os.path.join(os.path.dirname(__file__), "..", "themes", "pmb.json")
theme = load_theme(TEMA)
engine = ChatbotEngine(theme)


def test_preprocess_normalisasi_dan_stopword():
    assert preprocess("Gmn cara bayar UKT, kak?") == ["bagaimana", "cara", "bayar", "ukt"]


def test_similarity_kalimat_sama_bernilai_satu():
    t = preprocess("jadwal pendaftaran")
    assert similarity(t, t) == pytest.approx(1.0)


def test_similarity_kalimat_berbeda_rendah():
    assert similarity(preprocess("beasiswa kip"), preprocess("jadwal tes")) < 0.45


def test_tema_valid():
    assert validate_theme(theme) == []


def test_validate_theme_menemukan_kesalahan():
    assert validate_theme({"id": "x"})


def test_tiap_intent_punya_pola_dan_respons():
    for i in theme["intents"]:
        assert len(i["patterns"]) >= 5
        assert i["responses"]


@pytest.mark.parametrize("kalimat,tag", [
    ("halo admin", "greeting"),
    ("menu utama", "greeting"),
    ("Kapan pendaftaran jalur reguler dibuka?", "jadwal_pendaftaran"),
    ("jadwal tes gelombang 2", "jadwal_pendaftaran"),
    ("Syarat masuknya apa saja?", "syarat_prosedur"),
    ("Berkas yang harus di-upload apa?", "syarat_prosedur"),
    ("Berapa biaya kuliah per semester?", "biaya_kuliah"),
    ("Uang pangkalnya berapa?", "biaya_kuliah"),
    ("Ada jurusan apa saja?", "daftar_prodi"),
    ("Apakah ada beasiswa KIP?", "info_beasiswa"),
])
def test_klasifikasi_intent(kalimat, tag):
    assert engine.classify(kalimat)[0] == tag


@pytest.mark.parametrize("angka,tag", [
    ("1", "jadwal_pendaftaran"), ("2", "syarat_prosedur"), ("3", "biaya_kuliah"),
    ("4", "daftar_prodi"), ("5", "info_beasiswa"),
])
def test_menu_angka(angka, tag):
    assert engine.classify(angka)[0] == tag


def test_salah_ketik_masih_dikenali():
    assert engine.classify("jadwl pendaftaran")[0] == "jadwal_pendaftaran"


@pytest.mark.parametrize("kalimat", [
    "Kapan ada open house?", "Info asrama", "siapa presiden indonesia",
])
def test_pertanyaan_di_luar_tema_fallback(kalimat):
    tag, _ = engine.classify(kalimat)
    assert tag is None
    assert "belum memahami" in engine.reply(kalimat)["reply"]
