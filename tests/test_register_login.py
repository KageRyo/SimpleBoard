import tests.env  # 確保先載入 localtest.env
import pytest
from .fixtures import client
import os
from app.schemas import CreateLoginSchema

TEST_USERNAME = os.environ.get("TEST_USER", "testuser")
TEST_PASSWORD = os.environ.get("TEST_PASS", "testpass")

def test_register(client):
    # GIVEN 尚未註冊的帳號
    payload = CreateLoginSchema(username=TEST_USERNAME, password=TEST_PASSWORD).dict()
    # WHEN 註冊新帳號
    resp = client.post("/register", json=payload)
    # THEN 應註冊成功
    assert resp.status_code == 200
    assert resp.json()["username"] == TEST_USERNAME

def test_register_duplicate(client):
    # GIVEN 已存在的帳號
    payload = CreateLoginSchema(username=TEST_USERNAME, password=TEST_PASSWORD).dict()
    # WHEN 再次註冊相同帳號
    resp = client.post("/register", json=payload)
    # THEN 應回傳 400
    assert resp.status_code == 400

def test_login_success(client):
    # GIVEN 已註冊的帳號
    payload = CreateLoginSchema(username=TEST_USERNAME, password=TEST_PASSWORD).dict()
    # WHEN 正確登入
    resp = client.post("/login", json=payload)
    # THEN 應取得 access 與 refresh token
    assert resp.status_code == 200
    data = resp.json()
    assert "access" in data and "refresh" in data

def test_login_fail(client):
    # GIVEN 已註冊的帳號
    payload = CreateLoginSchema(username=TEST_USERNAME, password="wrongpass").dict()
    # WHEN 密碼錯誤登入
    resp = client.post("/login", json=payload)
    # THEN 應回傳 401
    assert resp.status_code == 401

def test_refresh_token(client):
    # GIVEN 已取得 refresh token
    payload = CreateLoginSchema(username=TEST_USERNAME, password=TEST_PASSWORD).dict()
    resp = client.post("/login", json=payload)
    refresh_token = resp.json()["refresh"]
    # WHEN 使用 refresh token 取得新 token
    resp = client.post("/refresh", params={"refresh": refresh_token})
    # THEN 應取得新的 access 與 refresh token
    assert resp.status_code == 200
    data = resp.json()
    assert "access" in data and "refresh" in data

def test_refresh_token_invalid(client):
    # GIVEN 無效的 refresh token
    # WHEN 嘗試 refresh
    resp = client.post("/refresh", params={"refresh": "invalidtoken"})
    # THEN 應回傳 401
    assert resp.status_code == 401