import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Header, status
from backend.app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    GenericAuthResponse
)
from backend.app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from backend.app.core.config import settings

router = APIRouter()

# shortcut: In-memory store for MVP / test suite, upgrade to SQLAlchemy User model when DB connected
MOCK_USERS_DB: Dict[str, Dict[str, Any]] = {
    "0912345678": {
        "user_id": "usr-seed-001",
        "full_name": "Nguyễn Văn A",
        "phone": "0912345678",
        "email": "vana@example.com",
        "hashed_password": hash_password("Password123@"),
        "role": "user",
        "created_at": "2026-11-06T08:00:00Z"
    }
}

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=GenericAuthResponse)
async def register(payload: UserRegisterRequest):
    if payload.phone in MOCK_USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "PHONE_ALREADY_EXISTS", "message": "Số điện thoại đã được đăng ký"}
        )

    user_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    user_record = {
        "user_id": user_id,
        "full_name": payload.full_name,
        "phone": payload.phone,
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
        "role": payload.role,
        "created_at": now_iso
    }
    MOCK_USERS_DB[payload.phone] = user_record

    return GenericAuthResponse(
        success=True,
        data={
            "user_id": user_id,
            "full_name": payload.full_name,
            "phone": payload.phone,
            "role": payload.role,
            "created_at": now_iso
        },
        message="Đăng ký tài khoản thành công"
    )

@router.post("/login", response_model=GenericAuthResponse)
async def login(payload: UserLoginRequest):
    user = MOCK_USERS_DB.get(payload.phone)
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Số điện thoại hoặc mật khẩu không chính xác"}
        )

    token = create_access_token(
        data={"sub": user["user_id"], "phone": user["phone"], "role": user["role"]},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return GenericAuthResponse(
        success=True,
        data={
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "user_id": user["user_id"],
                "full_name": user["full_name"],
                "phone": user["phone"],
                "role": user["role"]
            }
        },
        message="Đăng nhập thành công"
    )

@router.get("/me", response_model=GenericAuthResponse)
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Yêu cầu Bearer token xác thực"}
        )

    token = authorization.split("Bearer ")[1].strip()
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_EXPIRED_OR_INVALID", "message": "Token không hợp lệ hoặc đã hết hạn"}
        )

    user = None
    for u in MOCK_USERS_DB.values():
        if u["user_id"] == payload.get("sub"):
            user = u
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "Người dùng không tồn tại"}
        )

    return GenericAuthResponse(
        success=True,
        data={
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "phone": user["phone"],
            "email": user.get("email"),
            "role": user["role"],
            "created_at": user["created_at"]
        }
    )
