import pytest
from .fixtures import client

def test_register(client):
    # GIVEN 尚未註冊的帳號
    # WHEN 註冊新帳號
    resp = client.post("/register", json={"username": "testuser", "password": "testpass"})
    # THEN 應註冊成功
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"

def test_register_duplicate(client):
    # GIVEN 已存在的帳號
    # WHEN 再次註冊相同帳號
    resp = client.post("/register", json={"username": "testuser", "password": "testpass"})
    # THEN 應回傳 400
    assert resp.status_code == 400

def test_login_success(client):
    # GIVEN 已註冊的帳號
    # WHEN 正確登入
    resp = client.post("/login", json={"username": "testuser", "password": "testpass"})
    # THEN 應取得 access 與 refresh token
    assert resp.status_code == 200
    data = resp.json()
    assert "access" in data and "refresh" in data

def test_login_fail(client):
    # GIVEN 已註冊的帳號
    # WHEN 密碼錯誤登入
    resp = client.post("/login", json={"username": "testuser", "password": "wrongpass"})
    # THEN 應回傳 401
    assert resp.status_code == 401

def test_refresh_token(client):
    # GIVEN 已取得 refresh token
    resp = client.post("/login", json={"username": "testuser", "password": "testpass"})
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
