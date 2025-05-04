import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from src.schemas import CreateMessageSchema, UpdateMessageSchema, MessageSchema
from src.database import Base, engine, SessionLocal
from src.models import Message
from typing import List

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
    
    
# 取得全部的留言
@app.get(
    "/messages",
    response_model=list[MessageSchema]
)
def get_all_messages(db: Session = Depends(get_db)):
    # 1. 讀取現有的留言(get or not)
    messages = db.query(Message).all()
    # 2. 回傳留言
    return messages


# 取得單一的留言
@app.get(
    "/message/{message_id}",
    response_model=MessageSchema
)
def get_message(message_id: int, db: Session = Depends(get_db)):
    # 1. 讀取現有的留言
    message = db.query(Message).filter(Message.id == message_id).first()
    # 2. 如果沒有找到，回傳 404 錯誤
    if not message:
        raise HTTPException(status_code=404, detail="找不到訊息")
    # 3. 回傳留言
    return message


# 新增留言
@app.post(
    "/message",
    response_model=MessageSchema
)
async def create_message(body: CreateMessageSchema, db: Session = Depends(get_db)):
    # 1. 讀取輸入的資料
    new_message = Message(
        username=body.username,
        message=body.message
    )
    # 2. 將資料存入資料庫
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    # 3. 回傳新增的留言
    return new_message


# 更新留言
@app.patch(
    "/message/{message_id}",
    response_model=MessageSchema
)
def update_message(message_id: int, body: UpdateMessageSchema, db: Session = Depends(get_db)):
    # 1. 拿出要更新的留言
    message = db.query(Message).filter(Message.id == message_id).first()
    # 2. 如果沒有找到，回傳 404 錯誤
    if not message:
        raise HTTPException(status_code=404, detail="找不到訊息")
    # 3. 更新留言的內容
    if body.username:
        message.username = body.username
    if body.message:
        message.message = body.message
    # 4. 儲存留言
    db.commit()
    db.refresh(message)
    # 5. 回傳更新的留言
    return message


# 刪除留言
@app.delete(
    "/message/{message_id}",
)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    # 1. 找出要刪除的留言
    message = db.query(Message).filter(Message.id == message_id).first()
    # 2. 如果沒有找到，回傳 404 錯誤
    if not message:
        raise HTTPException(status_code=404, detail="找不到訊息")
    # 3. 刪除留言
    db.delete(message)
    db.commit()
    # 4. 回傳刪除成功的訊息
    return Response(status_code=204)