import secrets

from jwt import encode, decode, PyJWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.schemas import CreateMessageSchema, UpdateMessageSchema, MessageSchema
from src.database import Base, engine, SessionLocal
from src.models import User, Message
from typing import List, Optional

app = FastAPI()


# 創建已經定義的資料表
Base.metadata.create_all(bind=engine)


# 密碼加密（Hashing）
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# JWT Token 的加密與解密
SECRET_KEY = secrets.token_urlsafe(32)  # 32 位元的隨機字串（動態產生）
ALGORITHM = "HS256"  # JWT 的加密演算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access Token 的有效時間（分鐘）
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Refresh Token 的有效時間（分鐘）（7 天）
# OAuth2 的 Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 取得資料庫的 Session 會話
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

# 實作密碼的加密與驗證
def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


# 產生 JWT Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
   
# 驗證 JWT Token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="無效的 Token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # 檢查 Token 是否有效
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    # 檢查使用者是否存在
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

   
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