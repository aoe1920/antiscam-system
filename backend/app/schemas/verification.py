from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EntityType(str, Enum):
    PHONE = "phone_number"
    BANK_ACCOUNT = "bank_account"
    QR_CODE = "qr_code"
    POST_CONTENT = "post_content"
    IMAGE_HASH = "image_hash"

class RiskLevel(str, Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"

class PenaltyBreakdown(BaseModel):
    graph_penalty: float = Field(0.0, description="Điểm phạt liên kết đồ thị (0-100), trọng số 0.40")
    psychology_penalty: float = Field(0.0, description="Điểm phạt thao túng tâm lý NLP (0-100), trọng số 0.25")
    community_penalty: float = Field(0.0, description="Điểm phạt lịch sử báo cáo cộng đồng (0-100), trọng số 0.20")
    image_penalty: float = Field(0.0, description="Điểm phạt băm tri giác ảnh lừa đảo pHash (0-100), trọng số 0.15")

class VietQRData(BaseModel):
    is_valid: bool = False
    bank_bin: Optional[str] = None
    account_number: Optional[str] = None
    amount: Optional[float] = None
    purpose: Optional[str] = None
    raw_payload: Optional[str] = None

class VerifyEntityRequest(BaseModel):
    entity_type: EntityType
    entity_value: str = Field(..., min_length=1, max_length=256)

class VerifyPostRequest(BaseModel):
    content: str = Field(..., description="Nội dung bài đăng, tin nhắn tuyển dụng hoặc cho thuê trọ")
    image_hashes: List[str] = Field(default_factory=list, description="Danh sách 64-bit hex pHash trích xuất từ ảnh")
    qr_payloads: List[str] = Field(default_factory=list, description="Chuỗi EMVCo Napas VietQR giải mã từ ảnh")
    phone_numbers: List[str] = Field(default_factory=list, description="Các số điện thoại phát hiện trong bài")
    bank_accounts: List[str] = Field(default_factory=list, description="Các số tài khoản phát hiện trong bài")

class VerificationResult(BaseModel):
    success: bool = True
    entity_type: str
    entity_value: str
    credit_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: RiskLevel
    penalties: PenaltyBreakdown
    detected_patterns: List[str] = Field(default_factory=list)
    what_if_scenarios: List[str] = Field(default_factory=list)
    trigger_sos: bool = False
    graph_depth: int = 0
    message: str = "Thẩm định hoàn tất"
