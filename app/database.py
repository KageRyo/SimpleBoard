from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.env import get_env

SQLALCHEMY_DATABASE_URL = get_env("APP_DATABASE_URL", "sqlite:///./message.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()