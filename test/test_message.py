import pytest
from .fixtures import client, user_token, auth_header

def test_create_message(client, user_token):
    # GIVEN 已登入的使用者
    # WHEN 發送新增留言請求
    resp = client.post("/message", json={"message": "hello world"}, headers=auth_header(user_token))
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
    resp = client.post("/message", json={"message": "get single"}, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # WHEN 查詢該留言
    resp = client.get(f"/message/{msg_id}", headers=auth_header(user_token))
    # THEN 應取得該留言內容
    assert resp.status_code == 200
    assert resp.json()["id"] == msg_id

def test_update_message(client, user_token):
    # GIVEN 已登入的使用者，且有一則留言
    resp = client.post("/message", json={"message": "to update"}, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # WHEN 更新該留言
    resp = client.patch(f"/message/{msg_id}", json={"message": "updated"}, headers=auth_header(user_token))
    # THEN 應成功更新留言內容
    assert resp.status_code == 200
    assert resp.json()["message"] == "updated"

def test_delete_message(client, user_token):
    # GIVEN 已登入的使用者，且有一則留言
    resp = client.post("/message", json={"message": "to delete"}, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # WHEN 刪除該留言
    resp = client.delete(f"/message/{msg_id}", headers=auth_header(user_token))
    # THEN 應成功刪除留言
    assert resp.status_code == 204

def test_edit_other_user_message(client, user_token):
    # GIVEN 另一個使用者已註冊並登入
    client.post("/register", json={"username": "otheruser", "password": "otherpass"})
    resp = client.post("/login", json={"username": "otheruser", "password": "otherpass"})
    other_token = resp.json()["access"]
    # 且 msguser 新增一則留言
    resp = client.post("/message", json={"message": "not yours"}, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # WHEN 其他使用者嘗試編輯該留言
    resp = client.patch(f"/message/{msg_id}", json={"message": "hack"}, headers=auth_header(other_token))
    # THEN 應回傳 403 禁止
    assert resp.status_code == 403

def test_delete_other_user_message(client, user_token):
    # GIVEN 另一個使用者已註冊並登入
    client.post("/register", json={"username": "otheruser2", "password": "otherpass2"})
    resp = client.post("/login", json={"username": "otheruser2", "password": "otherpass2"})
    other_token = resp.json()["access"]
    # 且 msguser 新增一則留言
    resp = client.post("/message", json={"message": "not yours del"}, headers=auth_header(user_token))
    msg_id = resp.json()["id"]
    # WHEN 其他使用者嘗試刪除該留言
    resp = client.delete(f"/message/{msg_id}", headers=auth_header(other_token))
    # THEN 應回傳 403 禁止
    assert resp.status_code == 403
