import pytest

@pytest.fixture(scope="session", autouse=True)
def check_server_running():
    import requests

    try:
        requests.get("http://127.0.0.1:8000/")
    except Exception:
        pytest.exit("❌ 后端服务未启动，请先运行 FastAPI")