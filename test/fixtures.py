import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def user_token(client):
    # GIVEN 註冊新帳號
    client.post("/register", json={"username": "msguser", "password": "msgpass"})
    # WHEN 登入取得 token
    resp = client.post("/login", json={"username": "msguser", "password": "msgpass"})
    tokens = resp.json()
    # THEN 回傳 access token
    return tokens["access"]

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}
