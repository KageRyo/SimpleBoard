from fastapi import FastAPI
from app.database import Base, engine
from app.api.routes import router

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(router)