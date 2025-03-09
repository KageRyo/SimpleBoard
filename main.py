from fastapi import FastAPI
from src.schemas import CreateMessageSchema, MessageSchema

app = FastAPI()


@app.get("/")
async def root():
    return {
        "message": "Hello FastAPI!"
    }
    
@app.get("/test/{username}")
async def username_test(username):
    return {
        "message": f"Hello {username}!"
    }
    
@app.post("/test/message")
async def message_test(username, message):
    return {
        "message": 
            f"Hello {username}! Your message is {message}"
    }