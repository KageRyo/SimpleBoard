import tests.env  # Ensure localtest.env is loaded
import pytest
from .fixtures import client, user_token, auth_header
import os
from app.schemas import CreateMessageSchema, UpdateMessageSchema, MessageSchema

def test_create_message(client, user_token):
    # Given: Logged-in user
    data = CreateMessageSchema(message="hello world").dict()
    # When: Send create message request
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    # Then: Should create message successfully
    assert resp.status_code == 200
    assert resp.json()["message"] == "hello world"
    global message_id
    message_id = resp.json()["id"]

def test_get_all_messages(client, user_token):
    # When: Get all messages (no login required)
    resp = client.get("/messages")
    # Then: Should get message list
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_get_message(client, user_token):
    # Given: Logged-in user with a message
    data = CreateMessageSchema(message="get single").dict()
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # When: Get the message (no login required)
    resp = client.get(f"/message/{msg_id}")
    # Then: Should get the message content
    assert resp.status_code == 200
    assert resp.json()["id"] == msg_id

def test_update_message(client, user_token):
    # Given: Logged-in user with a message
    data = CreateMessageSchema(message="to update").dict()
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    update_data = {"message": "updated"}
    # When: Update the message
    resp = client.patch(f"/message/{msg_id}", json=update_data, headers=auth_header(user_token))
    # Then: Should update message successfully
    assert resp.status_code == 200
    assert resp.json()["message"] == "updated"

def test_delete_message(client, user_token):
    # Given: Logged-in user with a message
    data = CreateMessageSchema(message="to delete").dict()
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # When: Delete the message
    resp = client.delete(f"/message/{msg_id}", headers=auth_header(user_token))
    # Then: Should delete message successfully
    assert resp.status_code == 204

def test_edit_other_user_message(client, user_token):
    # Given: Another user is registered and logged in
    other_user = os.environ.get("TEST_OTHER_USER", "otheruser")
    other_pass = os.environ.get("TEST_OTHER_PASS", "otherpass")
    client.post("/register", json={"username": other_user, "password": other_pass})
    resp = client.post("/login", json={"username": other_user, "password": other_pass})
    other_token = resp.json()["access"]
    # And: msguser creates a message
    data = CreateMessageSchema(message="not yours").dict()
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # When: Other user tries to edit the message
    resp = client.patch(f"/message/{msg_id}", json={"message": "hack"}, headers=auth_header(other_token))
    # Then: Should return 403 Forbidden
    assert resp.status_code == 403

def test_delete_other_user_message(client, user_token):
    # Given: Another user is registered and logged in
    other_user = os.environ.get("TEST_OTHER_USER2", "otheruser2")
    other_pass = os.environ.get("TEST_OTHER_PASS2", "otherpass2")
    client.post("/register", json={"username": other_user, "password": other_pass})
    resp = client.post("/login", json={"username": other_user, "password": other_pass})
    other_token = resp.json()["access"]
    # And: msguser creates a message
    data = CreateMessageSchema(message="not yours del").dict()
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # When: Other user tries to delete the message
    resp = client.delete(f"/message/{msg_id}", headers=auth_header(other_token))
    # Then: Should return 403 Forbidden
    assert resp.status_code == 403
