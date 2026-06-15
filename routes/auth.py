import os
import sqlite3
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from database import get_db, init_db

router = APIRouter(tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "stocksage-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

def create_token(user_id: int, email: str):
    expire = datetime.utcnow() + timedelta(days=TOKEN_EXPIRE_DAYS)
    return jwt.encode({"user_id": user_id, "email": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return None

@router.post("/api/auth/register")
async def register(req: RegisterRequest, response: Response):
    conn = get_db()
    try:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (req.email,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        password_hash = pwd_context.hash(req.password)
        cursor = conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", (req.name, req.email, password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        token = create_token(user_id, req.email)
        response.set_cookie("auth_token", token, max_age=TOKEN_EXPIRE_DAYS*24*3600, httponly=True, samesite="lax")
        return {"success": True, "name": req.name, "email": req.email}
    finally:
        conn.close()

@router.post("/api/auth/login")
async def login(req: LoginRequest, response: Response):
    conn = get_db()
    try:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (req.email,)).fetchone()
        if not user or not pwd_context.verify(req.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token = create_token(user["id"], user["email"])
        response.set_cookie("auth_token", token, max_age=TOKEN_EXPIRE_DAYS*24*3600, httponly=True, samesite="lax")
        return {"success": True, "name": user["name"], "email": user["email"]}
    finally:
        conn.close()

@router.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie("auth_token")
    return {"success": True}

@router.get("/api/auth/me")
async def me(request: Request):
    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    conn = get_db()
    try:
        user = conn.execute("SELECT id, name, email, created_at FROM users WHERE id = ?", (payload["user_id"],)).fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return {"id": user["id"], "name": user["name"], "email": user["email"], "created_at": user["created_at"]}
    finally:
        conn.close()
