from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users" # 資料表名稱

    id = Column(Integer, primary_key=True, index=True) # 主鍵
    username = Column(String, unique=True, index=True) # 使用者名稱
    password = Column(String) # 使用者密碼
    
    messages = relationship("Message", back_populates="author") # 一對多的關聯，使用者可以有多個留言
    

class Message(Base):
    __tablename__ = "messages" # 資料表名稱
    
    id = Column(Integer, primary_key=True, index=True) # 主鍵
    username = Column(String, ForeignKey("users.username"))
    message = Column(String) # 留言訊息
    
    author = relationship("User", back_populates="messages") # 一對多的關聯，留言者是使用者