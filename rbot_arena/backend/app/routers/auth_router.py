from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from app.auth.jwt import _USERS, _ROLES, hash_pw, verify_pw, create_token, seed_admin, require_user
from fastapi import Depends

router = APIRouter(prefix="/auth", tags=["auth"])
seed_admin()

class LoginReq(BaseModel):
    email: str
    password: str

class RegisterReq(BaseModel):
    email: str
    password: str
    role: str = "viewer"

@router.post("/register")
def register(body: RegisterReq):
    if body.email in _USERS:
        raise HTTPException(409, "User exists")
    _USERS[body.email] = hash_pw(body.password)
    _ROLES[body.email] = body.role
    return {"ok": True}

@router.post("/login")
def login(body: LoginReq, resp: Response):
    if body.email not in _USERS or not verify_pw(body.password, _USERS[body.email]):
        raise HTTPException(401, "Bad credentials")
    role = _ROLES.get(body.email, "viewer")
    access = create_token(body.email, role)
    refresh = create_token(body.email, role, refresh=True)
    # Set HttpOnly cookies for browser flows
    resp.set_cookie("access_token", access, httponly=True, samesite="lax")
    resp.set_cookie("refresh_token", refresh, httponly=True, samesite="lax")
    return {"access_token": access, "refresh_token": refresh, "role": role}

@router.post("/refresh")
def refresh_token(resp: Response, refresh_token: str):
    from app.auth.jwt import decode_token
    payload = decode_token(refresh_token, refresh=True)
    access = create_token(payload.sub, payload.role)
    resp.set_cookie("access_token", access, httponly=True, samesite="lax")
    return {"access_token": access}

@router.get("/me")
def me(user=Depends(require_user)):
    return user
