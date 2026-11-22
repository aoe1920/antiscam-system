from backend.app.services.graph_service import GraphService

def test_graph_direct_scam_phone():
    service = GraphService()
    penalty, depth, reason = service.query_entity_risk("0987654321")
    assert penalty == 100.0
    assert depth == 1
    assert "lừa đảo" in reason

def test_graph_indirect_burner_sim():
    service = GraphService()
    penalty, depth, reason = service.query_entity_risk("0909112233")
    assert penalty == 80.0
    assert depth == 2

def test_graph_safe_clean_phone():
    service = GraphService()
    penalty, depth, reason = service.query_entity_risk("0911999888")
    assert penalty == 0.0
    assert depth == 0
    assert reason is None
