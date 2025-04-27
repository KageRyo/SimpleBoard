from sqlalchemy import Column, Integer, String
from src.database import Base


class Message(Base):
    __tablename__ = "messages" # 資料表名稱
    
    id = Column(Integer, primary_key=True, index=True) # 主鍵
    username = Column(String, index=True) # 留言的人
    message = Column(String) # 留言訊息