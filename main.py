import pandas as pd
from fastapi import FastAPI, HTTPException
from src.schemas import CreateMessageSchema, MessageSchema

app = FastAPI()

# JSON 資料存儲
def load_message():
    try:
        df = pd.read_json("message.json")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        return []

def save_message(message):
    df = pd.DataFrame(message)
    df.to_json("message.json", orient="records")

# 測試程式碼
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