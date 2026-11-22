from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., description="Họ và tên đầy đủ")
    phone: str = Field(..., min_length=9, max_length=15, description="Số điện thoại")
    email: Optional[str] = Field(None, description="Địa chỉ email")
    password: str = Field(..., min_length=6, description="Mật khẩu tài khoản")
    role: str = Field("user", description="Vai trò: user | guardian | admin")

class UserLoginRequest(BaseModel):
    phone: str = Field(..., description="Số điện thoại đăng nhập")
    password: str = Field(..., description="Mật khẩu đăng nhập")

class UserResponseData(BaseModel):
    user_id: str
    full_name: str
    phone: str
    role: str
    email: Optional[str] = None
    created_at: str

class TokenResponseData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class GenericAuthResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]
    message: Optional[str] = None
