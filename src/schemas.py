from pydantic import BaseModel
from typing import Optional


"""
Schemas of the user
"""
class UserSchema(BaseModel):
    id: int
    username: str
    password: str

    class Config:
        orm_mode = True

class CreateLoginSchema(BaseModel):
    username: str   # 使用者名稱
    password: str   # 使用者密碼

class JwtTokenSchema(BaseModel):
    access: str   # Access Token
    refresh: str  # Refresh Token


"""
Schemas of the message
"""
class CreateMessageSchema(BaseModel):
    message: str    # 留言訊息
    
class UpdateMessageSchema(BaseModel):
    message: Optional[str] = None    # 留言訊息
    
class MessageSchema(BaseModel):
    # id 只在 GET 時使用，不加在 CreateMessageSchema 是因為這不是要讓使用者自己設定的欄位
    id: int         # id 是整數，所以我們要求格式是 int   
    username: str
    message: str
    
    class Config:   # 這個設定是讓 Pydantic 可以從 ORM 的物件轉換成 Pydantic 的物件
        orm_mode = True