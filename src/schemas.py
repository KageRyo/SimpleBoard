from pydantic import BaseModel
from typing import Optional


class CreateMessageSchema(BaseModel):
    username: str   # 留言的人
    message: str    # 留言訊息
    
    
class UpdateMessageSchema(BaseModel):
    username: Optional[str] = None   # 留言的人
    message: Optional[str] = None    # 留言訊息
    
    
class MessageSchema(BaseModel):
    # id 只在 GET 時使用，不加在 CreateMessageSchema 是因為這不是要讓使用者自己設定的欄位
    id: int         # id 是整數，所以我們要求格式是 int   
    username: str
    message: str