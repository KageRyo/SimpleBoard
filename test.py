import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 定義資料模型
class CreateMessageSchema(BaseModel):
    username: str
    message: str

class MessageSchema(BaseModel):
    id: int
    username: str
    message: str

# JSON 存儲工具函數
def load_messages():
    try:
        with open("messages.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_messages(messages):
    with open("messages.json", "w") as f:
        json.dump(messages, f)

# Create: 新增留言
@app.post("/messages/", response_model=MessageSchema)
async def create_message(msg: CreateMessageSchema):
    messages = load_messages()
    new_id = max([m["id"] for m in messages], default=0) + 1  # 自動生成 ID
    new_message = {
        "id": new_id,
        "username": msg.username,
        "message": msg.message
    }
    messages.append(new_message)
    save_messages(messages)
    return new_message

# Read: 讀取所有留言
@app.get("/messages/", response_model=list[MessageSchema])
async def get_messages():
    messages = load_messages()
    return messages

# Read: 讀取單一留言
@app.get("/messages/{message_id}", response_model=MessageSchema)
async def get_message(message_id: int):
    messages = load_messages()
    for m in messages:
        if m["id"] == message_id:
            return m
    raise HTTPException(status_code=404, detail="留言未找到")

# Update: 更新留言
@app.put("/messages/{message_id}", response_model=MessageSchema)
async def update_message(message_id: int, updated_msg: CreateMessageSchema):
    messages = load_messages()
    for i, m in enumerate(messages):
        if m["id"] == message_id:
            messages[i]["username"] = updated_msg.username
            messages[i]["message"] = updated_msg.message
            save_messages(messages)
            return messages[i]
    raise HTTPException(status_code=404, detail="留言未找到")

# Delete: 刪除留言
@app.delete("/messages/{message_id}")
async def delete_message(message_id: int):
    messages = load_messages()
    for i, m in enumerate(messages):
        if m["id"] == message_id:
            messages.pop(i)
            save_messages(messages)
            return {"message": "留言刪除成功"}
    raise HTTPException(status_code=404, detail="留言未找到")