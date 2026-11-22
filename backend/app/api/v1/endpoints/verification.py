from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from backend.app.schemas.verification import (
    EntityType,
    VerifyEntityRequest,
    VerifyPostRequest,
    VerificationResult,
)
from backend.app.services.verification_service import VerificationService
from backend.app.services.vision_service import VisionService

router = APIRouter(prefix="/verify", tags=["Verification"])

class VerifyEntityContractRequest(BaseModel):
    entity_type: str = Field(..., description="bank_account, phone_number, hoặc content_text")
    value: str = Field(..., min_length=1)
    bank_code: Optional[str] = None
    content_text: Optional[str] = None

class VietQRContractRequest(BaseModel):
    qr_payload: str

class ImageHashContractRequest(BaseModel):
    phash: str

# Dependency injection
def get_verification_service() -> VerificationService:
    return VerificationService()

@router.post("/entity", summary="Kiểm tra an toàn thực thể (Phone, Bank, Content)")
async def verify_entity(
    payload: VerifyEntityContractRequest,
    service: VerificationService = Depends(get_verification_service)
):
    # Mapping entity_type
    e_type_map = {
        "bank_account": EntityType.BANK_ACCOUNT,
        "phone_number": EntityType.PHONE,
        "content_text": EntityType.POST_CONTENT,
        "qr_code": EntityType.QR_CODE
    }
    e_type = e_type_map.get(payload.entity_type.lower(), EntityType.PHONE)

    # Nếu có kèm theo content_text (tra cứu kết hợp nội dung tin nhắn)
    if payload.content_text:
        req = VerifyPostRequest(
            content=payload.content_text,
            phone_numbers=[payload.value] if e_type == EntityType.PHONE else [],
            bank_accounts=[payload.value] if e_type == EntityType.BANK_ACCOUNT else []
        )
        res = service.verify_post(req)
        res.entity_value = payload.value
        res.entity_type = payload.entity_type
        return {
            "success": True,
            "data": res.model_dump(),
            "message": "Thẩm định thực thể kèm ngữ cảnh hoàn tất"
        }

    # Fast-Path kiểm tra thực thể độc lập
    req = VerifyEntityRequest(
        entity_type=e_type,
        entity_value=payload.value
    )
    res = service.verify_single_entity(req)
    return {
        "success": True,
        "data": res.model_dump(),
        "message": "Thẩm định nhanh thực thể hoàn tất"
    }

@router.post("/vietqr", summary="Bóc tách mã thanh toán VietQR Napas EMVCo")
async def verify_vietqr(payload: VietQRContractRequest):
    data = VisionService.parse_vietqr_tlv(payload.qr_payload)
    if not data.is_valid:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_QR_PAYLOAD", "message": "Chuỗi mã QR không đúng định dạng chuẩn VietQR/Napas"}
        )

    bank_name = VisionService.KNOWN_BANKS.get(data.bank_bin or "", "Ngân hàng liên kết Napas")
    return {
        "success": True,
        "data": {
            "bank_bin": data.bank_bin,
            "bank_name": bank_name,
            "account_number": data.account_number,
            "amount": data.amount,
            "purpose": data.purpose
        },
        "message": "Bóc tách mã VietQR thành công"
    }

@router.post("/image-phash", summary="So khớp mã băm tri giác ảnh lừa đảo")
async def verify_image_phash(payload: ImageHashContractRequest):
    known_hashes = ["a1b2c3d4e5f60718", "ffff0000aaaa5555", "1234567890abcdef"]
    penalty, min_dist, matched = VisionService.evaluate_image_similarity(payload.phash, known_hashes)

    is_duplicate = min_dist <= 10
    return {
        "success": True,
        "data": {
            "calculated_phash": payload.phash,
            "is_duplicate_scam_image": is_duplicate,
            "min_hamming_distance": min_dist,
            "matched_report_id": "rep_987654" if is_duplicate else None,
            "matched_image_url": "https://storage.antiscam.vn/evidence/img_01.jpg" if is_duplicate else None,
            "penalty_score": penalty
        },
        "message": "So khớp ảnh thành công"
    }

@router.post("/post", summary="Thẩm định toàn diện bài đăng đa kênh (Web deep audit)")
async def verify_post(
    payload: VerifyPostRequest,
    service: VerificationService = Depends(get_verification_service)
):
    res = service.verify_post(payload)
    return {
        "success": True,
        "data": res.model_dump(),
        "message": "Thẩm định bài đăng đa kênh hoàn tất"
    }
