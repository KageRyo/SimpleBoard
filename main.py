import pandas as pd
from fastapi import FastAPI, HTTPException
from src.schemas import CreateMessageSchema, MessageSchema

app = FastAPI()


# JSON 資料存儲
def load_message():
    try:
        df = pd.read_json("message.json")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        return []

def save_message(message):
    df = pd.DataFrame(message)
    df.to_json("message.json", orient="records")


# 新增留言
@app.post(
    "/message",
    response_model=MessageSchema
)
async def create_message(body: CreateMessageSchema):
    # 1. 讀取現有的留言(get or not)
    messages = load_message()
    # 2. 處理 ID
    new_id = max([message["id"] for message in messages], default=0) + 1
    # 3. 新增留言
    mew_message = MessageSchema(
        id = new_id,
        username = body.username,
        message = body.message
    ).dict()
    messages.append(mew_message)
    # 4. 儲存留言
    save_message(messages)
    # 5. 回傳新增的留言
    return mew_message


# 測試程式碼
@app.get("/")
async def root():
    return {
        "message": "Hello FastAPI!"
    }
    
@app.get("/test/{username}")
async def username_test(username):
    return {
        "message": f"Hello {username}!"
    }
    
@app.post("/test/message")
async def message_test(username, message):
    return {
        "message": 
            f"Hello {username}! Your message is {message}"
    }