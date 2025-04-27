import pandas as pd
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from src.schemas import CreateMessageSchema, UpdateMessageSchema, MessageSchema
from src.database import Base, engine, SessionLocal

app = FastAPI()


# 創建已經定義的資料表
Base.metadata.create_all(bind=engine)


# 取得資料庫的 Session 會話
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    
    
# 取得全部的留言
@app.get(
    "/messages",
    response_model=list[MessageSchema]
)
def get_all_messages():
    # 1. 讀取現有的留言(get or not)
    messages = load_message()
    # 2. 回傳留言
    return messages


# 取得單一的留言
@app.get(
    "/message/{message_id}",
    response_model=MessageSchema
)
def get_message(message_id: int):
    # 1. 先取得全部的留言
    messages = load_message()
    # 2. 找到對應的留言(依照 message_id)
    for index in messages:
        if index["id"] == message_id:
            return index
    # 3. 如果沒有找到，回傳 404 錯誤
    raise HTTPException(status_code=404, detail="找不到訊息")


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


# 更新留言
@app.patch(
    "/message/{message_id}",
    response_model=MessageSchema
)
def update_message(message_id: int, body: UpdateMessageSchema):
    # 1. 取得全部的留言
    messages = load_message()
    # 2. 找到對應的留言(依照 message_id)
    for index, message in enumerate(messages):
        if message["id"] == message_id:
            if body.username:
                messages[index]["username"] = body.username
            if body.message:
                messages[index]["message"] = body.message
            # 3. 儲存留言
            save_message(messages)
            # 4. 回傳更新的留言
            return messages[index]
    # 5. 如果沒有找到，回傳 404 錯誤
    raise HTTPException(status_code=404, detail="找不到訊息")


# 刪除留言
@app.delete(
    "/message/{message_id}",
)
def delete_message(message_id: int):
    # 1. 取得全部的留言
    messages = load_message()
    # 2. 找到對應的留言(依照 message_id)
    for index, message in enumerate(messages):
        if message["id"] == message_id:
            # 3. 刪除留言
            del messages[index]
            # 4. 儲存留言
            save_message(messages)
            # 5. 回傳成功訊息
            return HTTPException(status_code=204, detail="刪除成功")