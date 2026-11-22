from typing import Tuple
from backend.app.schemas.verification import RiskLevel, PenaltyBreakdown

class ScoringService:
    W_GRAPH = 0.40
    W_PSYCHOLOGY = 0.25
    W_COMMUNITY = 0.20
    W_IMAGE = 0.15

    @classmethod
    def calculate_score(
        cls,
        s_g: float = 0.0,
        s_p: float = 0.0,
        s_s: float = 0.0,
        s_i: float = 0.0
    ) -> Tuple[float, RiskLevel, PenaltyBreakdown, bool]:
        """
        Tính toán điểm tín nhiệm dựa trên 4 chiều trọng số:
        P = w_g * s_g + w_p * s_p + w_s * s_s + w_i * s_i
        Score = 100 - P
        """
        # Đảm bảo các điểm phạt nằm trong thang 0.0 - 100.0
        s_g = max(0.0, min(100.0, float(s_g)))
        s_p = max(0.0, min(100.0, float(s_p)))
        s_s = max(0.0, min(100.0, float(s_s)))
        s_i = max(0.0, min(100.0, float(s_i)))

        total_penalty = (
            cls.W_GRAPH * s_g +
            cls.W_PSYCHOLOGY * s_p +
            cls.W_COMMUNITY * s_s +
            cls.W_IMAGE * s_i
        )

        score = round(max(0.0, 100.0 - min(100.0, total_penalty)), 1)

        # Nếu có liên kết trực tiếp với thực thể tội phạm đã xác minh (s_g == 100)
        # hoặc tổng điểm phạt vượt mức nghiêm trọng, kích hoạt CRITICAL theo SRS
        if s_g >= 100.0:
            score = min(score, 15.0)
            level = RiskLevel.CRITICAL
            trigger_sos = True
        elif score >= 80.0:
            level = RiskLevel.SAFE
            trigger_sos = False
        elif score >= 50.0:
            level = RiskLevel.CAUTION
            trigger_sos = False
        elif score >= 25.0:
            level = RiskLevel.HIGH_RISK
            trigger_sos = False
        else:
            level = RiskLevel.CRITICAL
            trigger_sos = True

        penalties = PenaltyBreakdown(
            graph_penalty=s_g,
            psychology_penalty=s_p,
            community_penalty=s_s,
            image_penalty=s_i
        )

        return score, level, penalties, trigger_sos
