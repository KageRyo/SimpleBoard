from jwt import decode, PyJWTError
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.schemas import CreateMessageSchema, UpdateMessageSchema, MessageSchema
from app.models import User, Message

from app.api.api_utils import get_current_user, get_db, SECRET_KEY, ALGORITHM

router = APIRouter()
oauth2_scheme = APIKeyHeader(name="Authorization")

@router.get("/messages", response_model=list[MessageSchema])
def get_all_messages(
    db: Session = Depends(get_db)
):
    # Get all messages with valid username
    messages = db.query(Message).filter(Message.username != None).all()
    return messages

@router.get("/message/{message_id}", response_model=MessageSchema)
def get_message(
    message_id: int,
    db: Session = Depends(get_db)
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
    # Create a new message for current user
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
    # Only allow user to update their own message
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
    # Only allow user to delete their own message
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="找不到訊息")
    if message.username != current_user.username:
        raise HTTPException(status_code=403, detail="只能刪除自己的留言")
    db.delete(message)
    db.commit()
    return Response(status_code=204)
