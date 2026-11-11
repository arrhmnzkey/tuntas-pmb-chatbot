import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "t.db")})
    return app.test_client()


def test_halaman_utama(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"TUNTAS PMB" in r.data


def test_api_chat_berhasil(client):
    r = client.post("/api/chat", json={"message": "berapa biaya kuliah"})
    assert r.status_code == 200
    assert r.get_json()["intent"] == "biaya_kuliah"


@pytest.mark.parametrize("payload", [{}, {"message": ""}, {"message": "   "}, {"message": "a" * 501}])
def test_api_chat_input_tidak_valid(client, payload):
    assert client.post("/api/chat", json=payload).status_code == 400


def test_api_chat_bukan_json(client):
    assert client.post("/api/chat", data="halo").status_code == 400


def test_riwayat_tersimpan_dan_bisa_dihapus(client):
    client.post("/api/chat", json={"message": "halo"})
    assert len(client.get("/api/history").get_json()) == 2
    client.delete("/api/history")
    assert client.get("/api/history").get_json() == []


def test_statistik_dan_admin(client):
    client.post("/api/chat", json={"message": "beasiswa"})
    client.post("/api/chat", json={"message": "kapan ada open house"})
    s = client.get("/api/stats").get_json()
    assert s["total"] == 2 and s["tidak_dikenali"] == 1
    page = client.get("/admin")
    assert page.status_code == 200 and b"open house" in page.data


def test_admin_key_melindungi_admin(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "t.db"), "ADMIN_KEY": "rahasia"})
    c = app.test_client()
    assert c.get("/admin").status_code == 403
    assert c.get("/admin?key=rahasia").status_code == 200


def test_xss_tersimpan_sebagai_teks_di_admin(client):
    client.post("/api/chat", json={"message": "<script>alert(1)</script>"})
    assert b"<script>alert(1)</script>" not in client.get("/admin").data
