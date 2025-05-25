from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users" # 資料表名稱

    id = Column(Integer, primary_key=True, index=True) # 主鍵
    username = Column(String, unique=True, index=True) # 使用者名稱
    password = Column(String) # 使用者密碼
    
    messages = relationship(
        "Message",
        back_populates="user",
        passive_deletes=True  # 讓 ondelete="SET NULL" 生效
    ) # 一對多的關聯，使用者可以有多個留言
    

class Message(Base):
    __tablename__ = "messages" # 資料表名稱
    
    id = Column(Integer, primary_key=True, index=True) # 主鍵
    username = Column(
        String,
        ForeignKey("users.username", ondelete="SET NULL"),
        nullable=True
    )  # 加上 ForeignKey 並允許為 None
    message = Column(Text, nullable=False) # 留言訊息
    
    user = relationship("User", back_populates="messages") # 一對多的關聯，留言者是使用者