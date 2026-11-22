from typing import Tuple, Dict, Any, Optional, List

class GraphService:
    """
    Dịch vụ truy vấn đồ thị tri thức mạng lưới gian lận (Neo4j Multi-hop Traversal).
    Hỗ trợ chế độ In-Memory Mock Graph phục vụ kiểm thử cục bộ và CI/CD độc lập.
    """

    # Mẫu đồ thị nội bộ giả lập các đường dây lừa đảo (Seed Syndicates)
    IN_MEMORY_SCAM_ENTITIES = {
        # Số điện thoại lừa đảo trực tiếp (k=1)
        "0987654321": {"depth": 1, "penalty": 100.0, "reason": "Số điện thoại đã bị tố cáo trong vụ án lừa đảo cọc phòng trọ Q.10"},
        "0912345678": {"depth": 1, "penalty": 100.0, "reason": "Số điện thoại giả mạo cơ quan điều tra Bộ Công An"},
        # Số tài khoản ngân hàng gian lận trực tiếp (k=1)
        "1029384756": {"depth": 1, "penalty": 100.0, "reason": "Tài khoản thụ hưởng napas của đường dây cọc căn hộ ảo"},
        "9876543210": {"depth": 1, "penalty": 100.0, "reason": "Tài khoản nhận tiền nhiệm vụ CTV Shopee lừa đảo"},
        # Thực thể liên kết gián tiếp cấp 2 (k=2: dùng chung thiết bị hoặc trung gian với tài khoản đen)
        "0909112233": {"depth": 2, "penalty": 80.0, "reason": "SIM rác liên kết cùng thiết bị đăng ký tài khoản 1029384756"},
        "1903678912": {"depth": 2, "penalty": 80.0, "reason": "Tài khoản trung gian nhận tiền luân chuyển từ 9876543210"},
        # Thực thể liên kết cấp 3 (k=3)
        "0701234567": {"depth": 3, "penalty": 50.0, "reason": "Nằm trong mạng lưới luân chuyển 3 bước của ổ nhóm lừa đảo"}
    }

    def __init__(self, neo4j_driver: Optional[Any] = None):
        self.driver = neo4j_driver

    def query_entity_risk(self, entity_value: str) -> Tuple[float, int, Optional[str]]:
        """
        Truy vấn rủi ro thực thể qua đồ thị liên kết đa bước (k <= 3 hops).
        Trả về: (graph_penalty 0-100, shortest_path_depth k, reason).
        """
        if not entity_value:
            return 0.0, 0, None

        normalized_value = entity_value.strip()

        # 1. Nếu có kết nối Neo4j thật, chạy Cypher query
        if self.driver is not None:
            try:
                with self.driver.session() as session:
                    cypher = """
                    MATCH (target {value: $value})
                    OPTIONAL MATCH path = shortestPath((target)-[*1..3]-(scam:ScamReport {status: 'VERIFIED'}))
                    RETURN length(path) AS depth, scam.description AS reason
                    LIMIT 1
                    """
                    record = session.run(cypher, value=normalized_value).single()
                    if record and record["depth"] is not None:
                        depth = int(record["depth"])
                        reason = record["reason"] or "Liên kết mạng lưới lừa đảo đã xác minh"
                        penalty = self._penalty_from_depth(depth)
                        return penalty, depth, reason
            except Exception:
                # Nếu Neo4j lỗi kết nối trong quá trình chạy, tự động fallback về in-memory
                pass

        # 2. In-Memory Mock Lookup (Cho Local Dev, Unit Testing, CI)
        if normalized_value in self.IN_MEMORY_SCAM_ENTITIES:
            data = self.IN_MEMORY_SCAM_ENTITIES[normalized_value]
            return data["penalty"], data["depth"], data["reason"]

        return 0.0, 0, None

    @staticmethod
    def _penalty_from_depth(depth: int) -> float:
        if depth == 1:
            return 100.0
        elif depth == 2:
            return 80.0
        elif depth == 3:
            return 50.0
        return 0.0
