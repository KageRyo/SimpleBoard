from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 設定資料庫的位址與連線方式(用來連線資料庫)
DB_URL = "sqlite:///./message.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

# 建立資料庫的 Session 會話(用來操作資料庫)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立資料庫的 Base 類別(ORM -> 用來定義資料表)
Base = declarative_base()