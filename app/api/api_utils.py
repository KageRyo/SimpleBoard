from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from jwt import decode, PyJWTError
from fastapi.security import APIKeyHeader
from app.models import User
from app.database import SessionLocal
from app.env import get_env

oauth2_scheme = APIKeyHeader(name="Authorization")

# Avoid circular import: get secret and algorithm directly from env
SECRET_KEY = get_env("APP_SECRET_KEY", "your-secret-key")
ALGORITHM = get_env("APP_ALGORITHM", "HS256")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # Parse JWT token and return current user, raise if invalid
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
