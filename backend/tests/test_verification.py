from backend.app.schemas.verification import (
    EntityType,
    RiskLevel,
    VerifyEntityRequest,
    VerifyPostRequest,
)
from backend.app.services.verification_service import VerificationService

def test_fast_path_verified_scam_phone():
    service = VerificationService()
    req = VerifyEntityRequest(
        entity_type=EntityType.PHONE,
        entity_value="0987654321"
    )
    result = service.verify_single_entity(req)
    assert result.success is True
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.credit_score < 50.0
    assert result.trigger_sos is True
    assert result.graph_depth == 1

def test_fast_path_clean_safe_phone():
    service = VerificationService()
    req = VerifyEntityRequest(
        entity_type=EntityType.PHONE,
        entity_value="0901239999"
    )
    result = service.verify_single_entity(req)
    assert result.success is True
    assert result.risk_level == RiskLevel.SAFE
    assert result.credit_score == 100.0
    assert result.trigger_sos is False

def test_deep_path_rental_scam_post_with_vietqr():
    service = VerificationService()
    req = VerifyPostRequest(
        content="Cho thuê phòng trọ cao cấp Q10 full nội thất, giá rẻ bất ngờ chỉ 2tr. Đang có nhiều người hỏi xem phòng, yêu cầu cọc giữ phòng trước 1 triệu vào tài khoản.",
        qr_payloads=["https://img.vietqr.io/image/970422-1029384756-compact2.png"],
        image_hashes=["a1b2c3d4e5f60718"]
    )
    result = service.verify_post(req)
    assert result.success is True
    # Có cả NLP lừa cọc + TK 1029384756 (trong black graph) + pHash trùng
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.trigger_sos is True
    assert len(result.detected_patterns) >= 2
    assert len(result.what_if_scenarios) == 3
