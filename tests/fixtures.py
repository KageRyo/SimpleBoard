import tests.env  # 確保先載入 localtest.env
import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
from app.schemas import CreateLoginSchema

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def user_token(client):
    username = os.environ.get("TEST_USER", "msguser")
    password = os.environ.get("TEST_PASS", "msgpass")
    # GIVEN 註冊新帳號
    payload = CreateLoginSchema(username=username, password=password).dict()
    client.post("/register", json=payload)
    # WHEN 登入取得 token
    resp = client.post("/login", json=payload)
    tokens = resp.json()
    # THEN 回傳 access token
    return tokens["access"]

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}
