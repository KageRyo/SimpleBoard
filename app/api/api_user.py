import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jwt import encode, decode, PyJWTError
from datetime import datetime, timedelta
from typing import Optional

from app.env import get_env
from app.database import SessionLocal
from app.models import User
from app.schemas import CreateLoginSchema, JwtTokenSchema, UserSchema

from passlib.context import CryptContext
from fastapi.security import APIKeyHeader

router = APIRouter()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = get_env("APP_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = get_env("APP_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_env("APP_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_MINUTES = int(get_env("APP_REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))

oauth2_scheme = APIKeyHeader(name="Authorization")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # Generate JWT access token with expiration
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    # Generate JWT refresh token with expiration
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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

@router.post("/register", response_model=UserSchema)
def register(body: CreateLoginSchema, db: Session = Depends(get_db)):
    # Register new user, fail if username exists
    user = db.query(User).filter(User.username == body.username).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_pw = hash_password(body.password)
    new_user = User(username=body.username, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=JwtTokenSchema)
def login(body: CreateLoginSchema, db: Session = Depends(get_db)):
    # Authenticate user and return tokens
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return {"access": access_token, "refresh": refresh_token}

@router.post("/refresh", response_model=JwtTokenSchema)
def refresh_token(refresh: str, db: Session = Depends(get_db)):
    # Issue new tokens using refresh token
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode(refresh, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return {"access": access_token, "refresh": refresh_token}

@router.delete("/delete")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Delete current user account
    db.delete(current_user)
    db.commit()
    return {"detail": "Account deleted"}
