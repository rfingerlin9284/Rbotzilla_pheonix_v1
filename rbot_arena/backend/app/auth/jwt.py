from datetime import datetime, timedelta, timezone
from typing import Optional, Literal
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, Header, Cookie
from pydantic import BaseModel
import os

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGO = "HS256"

JWT_SECRET = os.getenv("JWT_SECRET", "dev")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "dev_refresh")
EXP_MIN = int(os.getenv("JWT_EXPIRE_MIN", "30"))
REFRESH_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "14"))

# Toy in-memory store; swap for SQLite/Postgres later
_USERS = {}
_ROLES = {}  # email -> role: "viewer"|"trader"|"admin"

class TokenPayload(BaseModel):
    sub: str  # email
    role: Literal["viewer", "trader", "admin"]
    exp: int

def hash_pw(p):
    return pwd.hash(p)

def verify_pw(p, h):
    return pwd.verify(p, h)

def create_token(email: str, role: str, minutes=EXP_MIN, refresh=False):
    now = datetime.now(timezone.utc)
    exp = now + (timedelta(days=REFRESH_DAYS) if refresh else timedelta(minutes=minutes))
    payload = {"sub": email, "role": role, "exp": int(exp.timestamp())}
    secret = JWT_REFRESH_SECRET if refresh else JWT_SECRET
    return jwt.encode(payload, secret, algorithm=ALGO)

def decode_token(token: str, refresh=False) -> TokenPayload:
    try:
        data = jwt.decode(token, JWT_REFRESH_SECRET if refresh else JWT_SECRET, algorithms=[ALGO])
        return TokenPayload(**data)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def seed_admin():
    """Seed an admin user from environment variables"""
    email = os.getenv("SEED_ADMIN_EMAIL")
    pw = os.getenv("SEED_ADMIN_PASSWORD")
    if email and pw and email not in _USERS:
        _USERS[email] = hash_pw(pw)
        _ROLES[email] = "admin"

async def require_user(
    authorization: Optional[str] = Header(None),
    access_cookie: Optional[str] = Cookie(None, alias="access_token")
):
    """Dependency to require authenticated user"""
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    elif access_cookie:
        token = access_cookie
    if not token:
        raise HTTPException(401, "Missing token")
    payload = decode_token(token)
    return {"email": payload.sub, "role": payload.role}

def require_role(min_role: str):
    """Dependency factory to require minimum role"""
    order = {"viewer": 0, "trader": 1, "admin": 2}
    async def dep(user=Depends(require_user)):
        if order[user["role"]] < order[min_role]:
            raise HTTPException(403, "Insufficient role")
        return user
    return dep
