import os
import re
from typing import List, Dict, Any, Tuple

class NLPService:
    # Từ điển dấu hiệu thao túng tâm lý và lừa đảo theo 4 nhóm kịch bản chính
    SCAM_PATTERNS = {
        "RENTAL_DEPOSIT": {
            "name": "Lừa cọc phòng trọ / Căn hộ ma",
            "keywords": [
                r"cọc giữ (chỗ|phòng)",
                r"chuyển cọc (ngay|gấp)",
                r"nhiều người (đang|hỏi|xem)",
                r"không cọc là mất",
                r"chuyển khoản trước xem phòng sau",
                r"cọc thiện chí",
                r"giá rẻ bất ngờ",
                r"bao điện nước full nội thất giá \d+k"
            ],
            "penalty_weight": 35.0,
            "scenarios": [
                "Bước 1: Đối tượng tạo áp lực thời gian, khẳng định có nhiều khách khác đang chờ chuyển cọc phòng.",
                "Bước 2: Yêu cầu chuyển cọc giữ chỗ 500k - 2 triệu qua số tài khoản cá nhân thay vì đến xem phòng trực tiếp.",
                "Bước 3: Sau khi nhận tiền, đối tượng viện lý do chưa gặp được, yêu cầu đóng thêm tiền hợp đồng hoặc chặn liên lạc ngay lập tức."
            ]
        },
        "TASK_RECRUITMENT": {
            "name": "Tuyển dụng CTV ảo / Nhiệm vụ nạp tiền",
            "keywords": [
                r"việc nhẹ lương cao",
                r"cộng tác viên (shopee|tiki|lazada|tiktok)",
                r"hoa hồng \d+%",
                r"nạp tiền (làm|thực hiện) nhiệm vụ",
                r"đơn hàng ảo",
                r"hoàn tiền cả gốc lẫn lãi",
                r"thu nhập \d+00k/ngày"
            ],
            "penalty_weight": 40.0,
            "scenarios": [
                "Bước 1: Mồi nhử bằng các nhiệm vụ nhỏ đầu tiên (like/share, ấn theo dõi) và trả hoa hồng thật 20k - 50k để tạo lòng tin.",
                "Bước 2: Nâng cấp lên đơn hàng/nhiệm vụ tài chính lớn hơn, yêu cầu nạp tiền hàng triệu đến hàng chục triệu đồng.",
                "Bước 3: Viện cớ sai cú pháp, tài khoản bị treo, ép nạn nhân tiếp tục nạp số tiền gấp đôi để giải cứu trước khi cắt đứt liên lạc."
            ]
        },
        "AUTHORITY_IMPERSONATION": {
            "name": "Mạo danh công an / Viện kiểm sát / Tòa án",
            "keywords": [
                r"bộ công an",
                r"công an điều tra",
                r"lệnh bắt (tạm giam|khẩn cấp)",
                r"đường dây rửa tiền",
                r"tài khoản liên quan đến vụ án",
                r"chuyển tiền (để|vào) tài khoản tạm giữ",
                r"xác minh trong sạch",
                r"không được tiết lộ cho ai"
            ],
            "penalty_weight": 50.0,
            "scenarios": [
                "Bước 1: Gọi điện tự xưng cán bộ công an hoặc viện kiểm sát, thông báo số điện thoại/CCCD liên quan vụ án rửa tiền, ma túy.",
                "Bước 2: Đe dọa bắt tạm giam, gửi lệnh bắt giả mạo qua Zalo/Telegram và yêu cầu nạn nhân vào phòng kín gọi video call.",
                "Bước 3: Yêu cầu chuyển toàn bộ tiền tiết kiệm vào 'tài khoản an toàn của cơ quan điều tra' để xác minh rồi chiếm đoạt."
            ]
        },
        "URGENT_EMERGENCY": {
            "name": "Giả mạo người thân / Cấp cứu khẩn",
            "keywords": [
                r"(tai nạn|cấp cứu) đang nằm viện",
                r"cần tiền mổ gấp",
                r"chuyển tiền viện phí ngay",
                r"máy hết tiền gọi nhờ số lạ",
                r"nợ nóng bị giang hồ giữ"
            ],
            "penalty_weight": 45.0,
            "scenarios": [
                "Bước 1: Gọi điện hốt hoảng báo tin con/người thân bị tai nạn nguy kịch đang ở phòng cấp cứu bệnh viện.",
                "Bước 2: Yêu cầu chuyển tiền viện phí phẫu thuật khẩn cấp vào số tài khoản bác sĩ/bệnh viện giả mạo.",
                "Bước 3: Ngắt liên lạc ngay khi nạn nhân chưa kịp xác thực lại với nhà trường hoặc người thân."
            ]
        }
    }

    @classmethod
    def analyze_text_manipulation(cls, text: str) -> Tuple[float, List[str], List[str]]:
        """
        Phân tích văn bản tiếng Việt để trích xuất ý đồ thao túng tâm lý và sinh kịch bản What-If.
        Trả về (penalty 0-100, detected_patterns, what_if_scenarios).
        """
        if not text or not isinstance(text, str):
            return 0.0, [], []

        text_lower = text.lower()
        total_penalty = 0.0
        detected_patterns = []
        what_if_scenarios = []

        for category, config in cls.SCAM_PATTERNS.items():
            matched_keywords = []
            for pattern in config["keywords"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matched_keywords.append(pattern)

            if matched_keywords:
                detected_patterns.append(f"{config['name']} ({len(matched_keywords)} dấu hiệu)")
                # Tăng điểm phạt theo mức độ khớp
                total_penalty += config["penalty_weight"] + (len(matched_keywords) - 1) * 5.0
                if not what_if_scenarios:
                    what_if_scenarios = config["scenarios"]

        total_penalty = min(100.0, total_penalty)

        # Nếu không có mẫu What-If nào khớp nhưng có văn bản
        if not what_if_scenarios and detected_patterns:
            what_if_scenarios = [
                "Cảnh báo: Nội dung chứa các dấu hiệu thúc giục giao dịch bất thường.",
                "Khuyến nghị: Tuyệt đối không chuyển tiền đặt cọc trước khi gặp mặt trực tiếp tại địa chỉ xác thực."
            ]

        return round(total_penalty, 1), detected_patterns, what_if_scenarios
