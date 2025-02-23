from pydantic import BaseModel

class CreateMessageSchema(BaseModel):
    username: str   # 留言的人
    message: str    # 留言訊息
    
class MessageSchema(BaseModel):
    # id 只在 GET 時使用，不加在 CreateMessageSchema 是因為這不是要讓使用者自己設定的欄位
    id: int         # id 是整數，所以我們要求格式是 int   
    username: str
    message: str
    
# === 以下是測試程式碼 ===
# 正確
try:
    CreateMessageSchema(
        username = "阿勳老師",
        message = "我想學 Python"
    )
    print("通過 CreateMessageSchema 測試")
except Exception as error_message:
    print("CreateMessageSchema 錯誤", error_message)
# 錯誤: message 應該是字串，但是我們放了整數
try:
    CreateMessageSchema(
        username = "阿勳老師",
        message = 54321
    )
    print("通過 CreateMessageSchema 測試")
except Exception as error_message:
    print("CreateMessageSchema 錯誤", error_message)
# 錯誤: username 應該是字串，但是我們放了整數
try:
    CreateMessageSchema(
        username = 54321,
        message = "message耶耶耶"
    )
    print("通過 CreateMessageSchema 測試")
except Exception as error_message:
    print("CreateMessageSchema 錯誤", error_message)
# 錯誤: 缺少 username
try:
    CreateMessageSchema(
        message = "message耶耶耶"
    )
    print("通過 CreateMessageSchema 測試")
except Exception as error_message:
    print("CreateMessageSchema 錯誤", error_message)