from fastapi import FastAPI
from app.database import Base, engine
from app.api.routes import router

app = FastAPI()

# 初始化資料表
Base.metadata.create_all(bind=engine)

# 掛載所有 API 路由
app.include_router(router)