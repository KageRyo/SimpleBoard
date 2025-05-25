import tests.env
import pytest
from .fixtures import client
import os
from app.schemas import CreateLoginSchema

TEST_USERNAME = os.environ.get("TEST_USER", "testuser")
TEST_PASSWORD = os.environ.get("TEST_PASS", "testpass")

def delete_test_user(client):
    # When: Login to get access token
    payload = CreateLoginSchema(username=TEST_USERNAME, password=TEST_PASSWORD).dict()
    resp = client.post("/login", json=payload)
    if resp.status_code != 200:
        return
    access_token = resp.json()["access"]
    # When: Delete the account
    client.delete("/delete", headers={"Authorization": f"Bearer {access_token}"})

def test_register(client):
    # Given: Ensure account is deleted before test
    delete_test_user(client)
    # Given: An unregistered account
    payload = CreateLoginSchema(username=TEST_USERNAME, password=TEST_PASSWORD).dict()
    # When: Register a new account
    resp = client.post("/register", json=payload)
    # Then: Should register successfully
    assert resp.status_code == 200
    assert resp.json()["username"] == TEST_USERNAME
    # Given: The account already exists
    payload = CreateLoginSchema(username=TEST_USERNAME, password=TEST_PASSWORD).dict()
    # When: Register the same account again
    resp = client.post("/register", json=payload)
    # Then: Should return 400
    assert resp.status_code == 400
    # Given: Clean up after test
    delete_test_user(client)

def test_login_success(client):
    # Given: Ensure account exists
    payload = CreateLoginSchema(username=TEST_USERNAME, password=TEST_PASSWORD).dict()
    client.post("/register", json=payload)
    # When: Login with correct credentials
    resp = client.post("/login", json=payload)
    # Then: Should get access and refresh token
    assert resp.status_code == 200
    data = resp.json()
    assert "access" in data and "refresh" in data

def test_login_fail(client):
    # Given: Registered account
    payload = CreateLoginSchema(username=TEST_USERNAME, password="wrongpass").dict()
    # When: Login with wrong password
    resp = client.post("/login", json=payload)
    # Then: Should return 401
    assert resp.status_code == 401

def test_refresh_token(client):
    # Given: Ensure account exists and login to get refresh token
    payload = CreateLoginSchema(username=TEST_USERNAME, password=TEST_PASSWORD).dict()
    client.post("/register", json=payload)
    resp = client.post("/login", json=payload)
    assert resp.status_code == 200
    refresh_token = resp.json()["refresh"]
    # When: Use refresh token to get new tokens
    resp = client.post("/refresh", params={"refresh": refresh_token})
    # Then: Should get new access and refresh token
    assert resp.status_code == 200
    data = resp.json()
    assert "access" in data and "refresh" in data

def test_refresh_token_invalid(client):
    # Given: Invalid refresh token
    # When: Try to refresh
    resp = client.post("/refresh", params={"refresh": "invalidtoken"})
    # Then: Should return 401
    assert resp.status_code == 401