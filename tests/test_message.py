import tests.env  # 確保先載入 localtest.env
import pytest
from .fixtures import client, user_token, auth_header
import os
from app.schemas import CreateMessageSchema, UpdateMessageSchema, MessageSchema

def test_create_message(client, user_token):
    # GIVEN 已登入的使用者
    data = CreateMessageSchema(message="hello world").dict()
    # WHEN 發送新增留言請求
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    # THEN 應成功新增留言
    assert resp.status_code == 200
    assert resp.json()["message"] == "hello world"
    global message_id
    message_id = resp.json()["id"]

def test_get_all_messages(client, user_token):
    # GIVEN 已登入的使用者
    # WHEN 查詢所有留言
    resp = client.get("/messages", headers=auth_header(user_token))
    # THEN 應取得留言列表
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_get_message(client, user_token):
    # GIVEN 已登入的使用者，且有一則留言
    data = CreateMessageSchema(message="get single").dict()
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # WHEN 查詢該留言
    resp = client.get(f"/message/{msg_id}", headers=auth_header(user_token))
    # THEN 應取得該留言內容
    assert resp.status_code == 200
    assert resp.json()["id"] == msg_id

def test_update_message(client, user_token):
    # GIVEN 已登入的使用者，且有一則留言
    data = CreateMessageSchema(message="to update").dict()
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    update_data = {"message": "updated"}
    # WHEN 更新該留言
    resp = client.patch(f"/message/{msg_id}", json=update_data, headers=auth_header(user_token))
    # THEN 應成功更新留言內容
    assert resp.status_code == 200
    assert resp.json()["message"] == "updated"

def test_delete_message(client, user_token):
    # GIVEN 已登入的使用者，且有一則留言
    data = CreateMessageSchema(message="to delete").dict()
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # WHEN 刪除該留言
    resp = client.delete(f"/message/{msg_id}", headers=auth_header(user_token))
    # THEN 應成功刪除留言
    assert resp.status_code == 204

def test_edit_other_user_message(client, user_token):
    # GIVEN 另一個使用者已註冊並登入
    other_user = os.environ.get("TEST_OTHER_USER", "otheruser")
    other_pass = os.environ.get("TEST_OTHER_PASS", "otherpass")
    client.post("/register", json={"username": other_user, "password": other_pass})
    resp = client.post("/login", json={"username": other_user, "password": other_pass})
    other_token = resp.json()["access"]
    # 且 msguser 新增一則留言
    data = CreateMessageSchema(message="not yours").dict()
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # WHEN 其他使用者嘗試編輯該留言
    resp = client.patch(f"/message/{msg_id}", json={"message": "hack"}, headers=auth_header(other_token))
    # THEN 應回傳 403 禁止
    assert resp.status_code == 403

def test_delete_other_user_message(client, user_token):
    # GIVEN 另一個使用者已註冊並登入
    other_user = os.environ.get("TEST_OTHER_USER2", "otheruser2")
    other_pass = os.environ.get("TEST_OTHER_PASS2", "otherpass2")
    client.post("/register", json={"username": other_user, "password": other_pass})
    resp = client.post("/login", json={"username": other_user, "password": other_pass})
    other_token = resp.json()["access"]
    # 且 msguser 新增一則留言
    data = CreateMessageSchema(message="not yours del").dict()
    resp = client.post("/message", json=data, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # WHEN 其他使用者嘗試刪除該留言
    resp = client.delete(f"/message/{msg_id}", headers=auth_header(other_token))
    # THEN 應回傳 403 禁止
    assert resp.status_code == 403
