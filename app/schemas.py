from pydantic import BaseModel
from typing import Optional


class UserSchema(BaseModel):
    id: int
    username: str
    password: str

    class Config:
        orm_mode = True


class CreateLoginSchema(BaseModel):
    username: str
    password: str


class JwtTokenSchema(BaseModel):
    access: str
    refresh: str


class CreateMessageSchema(BaseModel):
    message: str


class UpdateMessageSchema(BaseModel):
    message: Optional[str] = None


class MessageSchema(BaseModel):
    id: int
    username: Optional[str]
    message: str

    class Config:
        orm_mode = True