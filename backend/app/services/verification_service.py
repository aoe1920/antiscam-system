import re
from typing import List, Optional
from backend.app.schemas.verification import (
    EntityType,
    RiskLevel,
    VerifyEntityRequest,
    VerifyPostRequest,
    VerificationResult,
    PenaltyBreakdown,
)
from backend.app.services.scoring_service import ScoringService
from backend.app.services.vision_service import VisionService
from backend.app.services.nlp_service import NLPService
from backend.app.services.graph_service import GraphService

class VerificationService:
    def __init__(self, graph_service: Optional[GraphService] = None):
        self.graph_service = graph_service or GraphService()

    def verify_single_entity(self, request: VerifyEntityRequest) -> VerificationResult:
        """
        [Fast-Path] Thẩm định tức thì một thực thể đơn lẻ (< 100 ms)
        Phục vụ trực tiếp cho CallScreeningService của Android và tra cứu nhanh.
        """
        val = request.entity_value.strip()
        e_type = request.entity_type

        # 1. Tra cứu đồ thị đa bước (Graph Traversal)
        s_g, depth, reason = self.graph_service.query_entity_risk(val)

        # 2. Điểm phạt cộng đồng (nếu có lý do xác minh)
        s_s = 60.0 if depth > 0 else 0.0

        # 3. Tính điểm tín nhiệm đa yếu tố
        score, level, penalties, trigger_sos = ScoringService.calculate_score(
            s_g=s_g,
            s_p=0.0,
            s_s=s_s,
            s_i=0.0
        )

        patterns = [reason] if reason else []
        scenarios = []
        if level in (RiskLevel.HIGH_RISK, RiskLevel.CRITICAL):
            scenarios = [
                f"Cảnh báo: Thực thể {val} liên kết với mạng lưới lừa đảo (khoảng cách {depth} bước).",
                "Hệ thống khuyến cáo: Tuyệt đối không nghe máy, không thực hiện chuyển khoản đến số tài khoản này."
            ]

        return VerificationResult(
            success=True,
            entity_type=e_type.value,
            entity_value=val,
            credit_score=score,
            risk_level=level,
            penalties=penalties,
            detected_patterns=patterns,
            what_if_scenarios=scenarios,
            trigger_sos=trigger_sos,
            graph_depth=depth,
            message="Thẩm định nhanh hoàn tất"
        )

    def verify_post(self, request: VerifyPostRequest) -> VerificationResult:
        """
        [Deep-Path] Thẩm định đa kênh bài đăng / tin nhắn chuyên sâu
        Tích hợp: Giải mã VietQR, so khớp ảnh pHash, NLP phân tích kịch bản và Graph Traversal.
        """
        all_phone_numbers = list(request.phone_numbers)
        all_bank_accounts = list(request.bank_accounts)
        detected_patterns = []

        # 1. Trích xuất tự động số điện thoại và STK từ nội dung văn bản nếu chưa có
        phones_in_text = re.findall(r"(?:0|\+84)[3|5|7|8|9][0-9]{8}\b", request.content)
        all_phone_numbers.extend(phones_in_text)

        accounts_in_text = re.findall(r"\b\d{9,16}\b", request.content)
        # Lọc bớt số điện thoại khỏi danh sách số tài khoản
        for acc in accounts_in_text:
            if acc not in all_phone_numbers:
                all_bank_accounts.append(acc)

        # 2. Giải mã chuỗi VietQR (nếu có)
        for qr in request.qr_payloads:
            qr_data = VisionService.parse_vietqr_tlv(qr)
            if qr_data.is_valid and qr_data.account_number:
                all_bank_accounts.append(qr_data.account_number)
                bank_name = VisionService.KNOWN_BANKS.get(qr_data.bank_bin or "", "Napas")
                detected_patterns.append(f"Mã VietQR thụ hưởng: {bank_name} - {qr_data.account_number}")

        # 3. Phân tích ảnh băm tri giác (pHash)
        # Giả lập một số hash ảnh lừa đảo mẫu đã biết trong kho
        known_scam_hashes = ["a1b2c3d4e5f60718", "ffff0000aaaa5555", "1234567890abcdef"]
        s_i = 0.0
        for h in request.image_hashes:
            p_img, dist, matched = VisionService.evaluate_image_similarity(h, known_scam_hashes)
            if p_img > s_i:
                s_i = p_img
                detected_patterns.append(f"Phát hiện ảnh căn hộ trùng lặp với kho lừa đảo (Hamming distance: {dist})")

        # 4. Phân tích NLP kịch bản thao túng tâm lý
        s_p, nlp_patterns, what_if_scenarios = NLPService.analyze_text_manipulation(request.content)
        detected_patterns.extend(nlp_patterns)

        # 5. Tra cứu đồ thị cho tất cả thực thể liên kết (Phone + Bank)
        max_s_g = 0.0
        max_depth = 0
        linked_entities = set(all_phone_numbers + all_bank_accounts)
        for entity in linked_entities:
            penalty, depth, reason = self.graph_service.query_entity_risk(entity)
            if penalty > max_s_g:
                max_s_g = penalty
                max_depth = depth
                if reason:
                    detected_patterns.append(f"Thực thể {entity}: {reason}")

        # 6. Điểm phạt cộng đồng nếu có liên kết đen
        s_s = 40.0 if max_depth > 0 else 0.0

        # 7. Tính tổng điểm tín nhiệm
        score, level, penalties, trigger_sos = ScoringService.calculate_score(
            s_g=max_s_g,
            s_p=s_p,
            s_s=s_s,
            s_i=s_i
        )

        return VerificationResult(
            success=True,
            entity_type="post_content",
            entity_value="post_analysis",
            credit_score=score,
            risk_level=level,
            penalties=penalties,
            detected_patterns=detected_patterns,
            what_if_scenarios=what_if_scenarios,
            trigger_sos=trigger_sos,
            graph_depth=max_depth,
            message="Thẩm định đa kênh bài đăng hoàn tất"
        )
