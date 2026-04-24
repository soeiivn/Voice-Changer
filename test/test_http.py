import requests

BASE = "http://127.0.0.1:8000"

def test_homepage():
    r = requests.get(f"{BASE}/")
    assert r.status_code == 200
    assert "html" in r.headers.get("Content-Type", "")

def test_app_page():
    r = requests.get(f"{BASE}/app")
    assert r.status_code == 200

def test_about_page():
    r = requests.get(f"{BASE}/about")
    assert r.status_code == 200

# ✅ 验证 WebSocket路径不能用HTTP访问（论文加分点）
def test_ws_http_invalid():
    r = requests.get(f"{BASE}/ws/audio")
    assert r.status_code == 404