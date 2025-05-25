from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    messages = relationship("Message", back_populates="user", passive_deletes=True)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(ForeignKey("users.username", ondelete="SET NULL"),  nullable=True)
    message = Column(Text, nullable=False)
    user = relationship("User", back_populates="messages")