from backend.app.services.vision_service import VisionService

def test_vietqr_url_parsing():
    url = "https://img.vietqr.io/image/970422-1029384756-compact2.png"
    data = VisionService.parse_vietqr_tlv(url)
    assert data.is_valid is True
    assert data.bank_bin == "970422"
    assert data.account_number == "1029384756"

def test_vietqr_emvco_tlv_parsing():
    # Chuỗi EMVCo mẫu đơn giản: 000201 (Payload) 5406100000 (Amount: 100000)
    raw_payload = "0002015406100000"
    data = VisionService.parse_vietqr_tlv(raw_payload)
    assert data.is_valid is True
    assert data.amount == 100000.0

def test_hamming_distance_identical():
    h1 = "a1b2c3d4e5f60718"
    h2 = "a1b2c3d4e5f60718"
    assert VisionService.hamming_distance(h1, h2) == 0

def test_hamming_distance_one_bit():
    h1 = "0000000000000000"
    h2 = "0000000000000001"
    assert VisionService.hamming_distance(h1, h2) == 1

def test_evaluate_image_similarity_match():
    known = ["a1b2c3d4e5f60718"]
    target = "a1b2c3d4e5f60719"  # 1 bit khác biệt
    penalty, dist, matched = VisionService.evaluate_image_similarity(target, known)
    assert dist == 1
    assert penalty > 90.0
    assert matched == "a1b2c3d4e5f60718"

def test_evaluate_image_similarity_safe():
    known = ["0000000000000000"]
    target = "ffffffffffffffff"  # 64 bits khác biệt
    penalty, dist, matched = VisionService.evaluate_image_similarity(target, known)
    assert dist == 64
    assert penalty == 0.0
    assert matched is None
