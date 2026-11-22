import re
from typing import Optional, List, Tuple
from backend.app.schemas.verification import VietQRData

class VisionService:
    # Danh mục BIN ngân hàng phổ biến tại Việt Nam (Napas)
    KNOWN_BANKS = {
        "970436": "Vietcombank",
        "970415": "VietinBank",
        "970418": "BIDV",
        "970405": "Agribank",
        "970422": "MBBank",
        "970407": "Techcombank",
        "970423": "TPBank",
        "970432": "VPBank",
        "970416": "ACB",
        "970441": "VIB",
        "970448": "OCB",
        "970403": "Sacombank",
        "970454": "VietCapitalBank",
        "970428": "NamABank",
        "970452": "Kienlongbank"
    }

    @classmethod
    def parse_vietqr_tlv(cls, payload: str) -> VietQRData:
        """
        Bóc tách chuỗi mã VietQR theo chuẩn EMVCo Napas (Tag-Length-Value).
        Bắt đầu bằng Tag 00 độ dài 02 giá trị '01'.
        """
        if not payload or not isinstance(payload, str):
            return VietQRData(is_valid=False)

        payload = payload.strip()
        # Kiểm tra nếu là URL VietQR rút gọn
        url_match = re.search(r"vietqr\.io/image/(\d+)-([A-Za-z0-9]+)", payload, re.IGNORECASE)
        if url_match:
            bank_bin = url_match.group(1)
            account_no = url_match.group(2)
            return VietQRData(
                is_valid=True,
                bank_bin=bank_bin,
                account_number=account_no,
                raw_payload=payload
            )

        if not payload.startswith("000201"):
            return VietQRData(is_valid=False, raw_payload=payload)

        result = VietQRData(is_valid=True, raw_payload=payload)
        idx = 0
        n = len(payload)

        try:
            while idx + 4 <= n:
                tag = payload[idx:idx+2]
                length = int(payload[idx+2:idx+4])
                idx += 4
                if idx + length > n:
                    break
                val = payload[idx:idx+length]
                idx += length

                # Tag 38: Thông tin tài khoản thụ hưởng Napas
                if tag == "38":
                    cls._parse_merchant_account_info(val, result)
                # Tag 54: Số tiền giao dịch
                elif tag == "54":
                    try:
                        result.amount = float(val)
                    except ValueError:
                        pass
                # Tag 62: Thông tin bổ sung (Nội dung chuyển khoản)
                elif tag == "62":
                    cls._parse_additional_data(val, result)

            return result
        except Exception:
            return VietQRData(is_valid=False, raw_payload=payload)

    @classmethod
    def _parse_merchant_account_info(cls, sub_payload: str, result: VietQRData) -> None:
        idx = 0
        n = len(sub_payload)
        while idx + 4 <= n:
            tag = sub_payload[idx:idx+2]
            length = int(sub_payload[idx+2:idx+4])
            idx += 4
            if idx + length > n:
                break
            val = sub_payload[idx:idx+length]
            idx += length

            if tag == "00":  # GUID Napas / AID
                pass
            elif tag == "01":  # Dịch vụ thụ hưởng: gồm BIN ngân hàng + Số tài khoản
                # Sub-TLV bên trong 01
                s_idx = 0
                s_n = len(val)
                while s_idx + 4 <= s_n:
                    s_tag = val[s_idx:s_idx+2]
                    s_len = int(val[s_idx+2:s_idx+4])
                    s_idx += 4
                    if s_idx + s_len > s_n:
                        break
                    s_val = val[s_idx:s_idx+s_len]
                    s_idx += s_len

                    if s_tag == "00":
                        result.bank_bin = s_val
                    elif s_tag == "01":
                        result.account_number = s_val
            elif tag == "02":
                result.account_number = val

    @classmethod
    def _parse_additional_data(cls, sub_payload: str, result: VietQRData) -> None:
        idx = 0
        n = len(sub_payload)
        while idx + 4 <= n:
            tag = sub_payload[idx:idx+2]
            length = int(sub_payload[idx+2:idx+4])
            idx += 4
            if idx + length > n:
                break
            val = sub_payload[idx:idx+length]
            idx += length
            if tag == "08":  # Purpose of transaction
                result.purpose = val

    @classmethod
    def hamming_distance(cls, hash1: str, hash2: str) -> int:
        """
        Tính khoảng cách Hamming giữa 2 mã băm tri giác 64-bit (16 ký tự hex).
        """
        try:
            val1 = int(hash1.strip(), 16)
            val2 = int(hash2.strip(), 16)
            xor_val = val1 ^ val2
            return bin(xor_val).count("1")
        except (ValueError, TypeError):
            return 64  # Khoảng cách tối đa nếu lỗi định dạng

    @classmethod
    def evaluate_image_similarity(cls, target_hash: str, scam_image_hashes: List[str]) -> Tuple[float, int, Optional[str]]:
        """
        So khớp mã băm target với kho ảnh gian lận đã xác minh.
        Ngưỡng phát hiện tương đồng cao: Hamming distance <= 10.
        Trả về (penalty 0-100, min_distance, matched_hash).
        """
        if not target_hash or not scam_image_hashes:
            return 0.0, 64, None

        min_dist = 64
        matched_hash = None

        for known_hash in scam_image_hashes:
            dist = cls.hamming_distance(target_hash, known_hash)
            if dist < min_dist:
                min_dist = dist
                matched_hash = known_hash

        # Ngưỡng chấp nhận trùng khớp biến thể: <= 10 bits khác biệt
        if min_dist <= 10:
            # min_dist = 0 -> penalty = 100
            # min_dist = 10 -> penalty = 50
            penalty = round(100.0 - (min_dist * 5.0), 1)
            return penalty, min_dist, matched_hash

        return 0.0, min_dist, None
