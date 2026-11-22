from backend.app.services.nlp_service import NLPService

def test_safe_normal_text():
    text = "Chào các bạn, hôm nay thời tiết Sài Gòn rất đẹp."
    penalty, patterns, scenarios = NLPService.analyze_text_manipulation(text)
    assert penalty == 0.0
    assert len(patterns) == 0

def test_rental_deposit_scam_detection():
    text = "Phòng trọ cao cấp Q10 full nội thất giá rẻ bất ngờ, đang có nhiều người hỏi xem phòng, ai cọc giữ phòng trước thì được."
    penalty, patterns, scenarios = NLPService.analyze_text_manipulation(text)
    assert penalty >= 35.0
    assert any("Lừa cọc phòng trọ" in p for p in patterns)
    assert len(scenarios) == 3

def test_recruitment_task_scam_detection():
    text = "Tuyển cộng tác viên Shopee việc nhẹ lương cao, hoàn tiền cả gốc lẫn lãi sau khi nạp tiền làm nhiệm vụ."
    penalty, patterns, scenarios = NLPService.analyze_text_manipulation(text)
    assert penalty >= 40.0
    assert any("Tuyển dụng CTV ảo" in p for p in patterns)

def test_authority_impersonation_detection():
    text = "Đây là cán bộ điều tra Bộ Công An, có lệnh bắt tạm giam đối tượng liên quan đường dây rửa tiền, chuyển tiền xác minh ngay."
    penalty, patterns, scenarios = NLPService.analyze_text_manipulation(text)
    assert penalty >= 50.0
    assert any("Mạo danh công an" in p for p in patterns)
