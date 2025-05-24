from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.schemas import CreateMessageSchema, UpdateMessageSchema, MessageSchema
from app.database import SessionLocal
from app.models import User, Message

router = APIRouter()
oauth2_scheme = APIKeyHeader(name="Authorization")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 複用 user 驗證
from app.api.api_user import SECRET_KEY, ALGORITHM
from jwt import decode, PyJWTError

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="無效的 Token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/messages", response_model=list[MessageSchema])
def get_all_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = db.query(Message).all()
    return messages

@router.get("/message/{message_id}", response_model=MessageSchema)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="找不到訊息")
    return message

@router.post("/message", response_model=MessageSchema)
async def create_message(
    body: CreateMessageSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_message = Message(
        username=current_user.username,
        message=body.message
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@router.patch("/message/{message_id}", response_model=MessageSchema)
def update_message(
    message_id: int,
    body: UpdateMessageSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="找不到訊息")
    if message.username != current_user.username:
        raise HTTPException(status_code=403, detail="只能編輯自己的留言")
    if body.message is not None:
        message.message = body.message
    db.commit()
    db.refresh(message)
    return message

@router.delete("/message/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="找不到訊息")
    if message.username != current_user.username:
        raise HTTPException(status_code=403, detail="只能刪除自己的留言")
    db.delete(message)
    db.commit()
    return Response(status_code=204)
