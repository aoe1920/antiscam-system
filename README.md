# SmartGuard — Hệ Thống Kiểm Chứng và Cảnh Báo Lừa Đảo Trực Tuyến

> **Đề tài:** Hệ thống kiểm chứng và cảnh báo lừa đảo trực tuyến bằng đồ thị liên kết thực thể  
> **Môn học:** Nhập môn Công nghệ Phần mềm (24_31) — Khoa Công nghệ Thông tin, Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM  
> **Giảng viên hướng dẫn:** ThS. Ngô Ngọc Đăng Khoa • **Nhóm thực hiện:** Nhóm 03  

[![Platform](https://img.shields.io/badge/Nền_tảng-Web_%7C_Android_Native-0d1117?style=flat-square&logo=android&logoColor=white)](#kiến-trúc-công-nghệ)
[![Backend](https://img.shields.io/badge/Máy_chủ-FastAPI_(Python_3.11)-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Graph DB](https://img.shields.io/badge/Cơ_sở_dữ_liệu_đồ_thị-Neo4j_5.18-008CC1?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com)
[![Relational DB](https://img.shields.io/badge/Cơ_sở_dữ_liệu_quan_hệ-PostgreSQL_16-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Frontend](https://img.shields.io/badge/Giao_diện_Web-Next.js_14-black?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![License: MIT](https://img.shields.io/badge/Giấy_phép-MIT-blue?style=flat-square)](LICENSE)

SmartGuard là nền tảng công nghệ phần mềm hỗ trợ phát hiện và cảnh báo sớm các hành vi lừa đảo trực tuyến đa phương thức. Hệ thống kết hợp giữa năng lực giám sát thời gian thực trên thiết bị di động Android và công nghệ phân tích đồ thị tri thức (Entity Knowledge Graph) trên máy chủ, nhằm bảo vệ hai nhóm đối tượng dễ bị tổn thương nhất trên không gian mạng: **học sinh, sinh viên tìm trọ/việc làm** và **người cao tuổi trong gia đình**.

---

## Mục Lục

- [1. Giới thiệu bài toán & Mục tiêu](#1-giới-thiệu-bài-toán--mục-tiêu)
- [2. Kiến trúc hệ thống & Phân tầng xử lý](#2-kiến-trúc-hệ-thống--phân-tầng-xử-lý)
- [3. Tính năng cốt lõi](#3-tính-năng-cốt-lõi)
- [4. Mô hình tính điểm tín nhiệm](#4-mô-hình-tính-điểm-tín-nhiệm)
- [5. Danh mục công nghệ sử dụng](#5-danh-mục-công-nghệ-sử-dụng)
- [6. Cấu trúc mã nguồn](#6-cấu-trúc-mã-nguồn)
- [7. Hướng dẫn cài đặt & Chạy thử](#7-hướng-dẫn-cài-đặt--chạy-thử)
- [8. Danh mục tài liệu kỹ thuật](#8-danh-mục-tài-liệu-kỹ-thuật)
- [9. Thành viên thực hiện](#9-thành-viên-thực-hiện)

---

## 1. Giới thiệu bài toán & Mục tiêu

Trong bối cảnh tội phạm công nghệ cao liên tục biến tướng, các đối tượng lừa đảo thường xuyên thay đổi số điện thoại rác (burner SIM) và tài khoản mạng xã hội ảo nhằm qua mặt các danh sách đen tĩnh. Tuy nhiên, các mắt xích cốt lõi bao gồm **số tài khoản ngân hàng thụ hưởng**, **kho ảnh chụp căn hộ/tuyển dụng** và **mô thức thao túng tâm lý** luôn có tính tái sử dụng và liên kết ngầm chặt chẽ.

**Mục tiêu của SmartGuard:**
1. **Chặn đứng từ xa:** Nhận diện và cảnh báo cuộc gọi mạo danh cơ quan công quyền, bệnh viện ngay trước khi phát chuông ($<\; 500\text{ ms}$).
2. **Vạch trần mạng lưới:** Mô hình hóa mối quan hệ giữa các thực thể vi phạm qua cơ sở dữ liệu đồ thị Neo4j, truy vết các đường dây lừa đảo liên kết đa bước ($k \;\le\; 3\text{ hops}$).
3. **Bảo vệ gia đình:** Tự động kích hoạt quy trình cảnh báo khẩn cấp SOS tới người thân bảo hộ khi người cao tuổi đàm thoại kéo dài với số máy nguy hiểm.
4. **Minh bạch hóa (Explainable AI):** Bóc tách mã VietQR Napas, đối soát ảnh trùng lặp bằng mã băm tri giác 64-bit `pHash`, và sinh chuỗi kịch bản giả định What-If giúp nạn nhân tỉnh táo nhận diện thủ đoạn.

---

## 2. Kiến trúc hệ thống & Phân tầng xử lý

Hệ thống được thiết kế theo kiến trúc phân tầng 2 lớp (Two-Tier Processing Pipeline) bảo đảm tối ưu hóa độ trễ thời gian thực và năng lực tính toán chuyên sâu:

```
                          KIẾN TRÚC TỔNG THỂ SMARTGUARD
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TẦNG THIẾT BỊ ĐẦU CUỐI                             │
│   [Android Client: CallScreening & FCM]    [Web Forensic Dashboard: Next.js]│
└──────────────────────┬───────────────────────────────────────┬──────────────┘
                       │ HTTPS / JSON                          │ HTTPS / WSS
                       ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       TẦNG MÁY CHỦ TRUNG TÂM (FASTAPI)                      │
│                                                                             │
│   ┌───────────────────────────────────┐ ┌─────────────────────────────────┐ │
│   │     FAST-PATH ENGINE (< 100 ms)   │ │     DEEP-PATH ENGINE            │ │
│   │  • Regex Validator & Local Cache  │ │  • Napas VietQR TLV Parser      │ │
│   │  • Direct Entity Blacklist Check  │ │  • 64-bit Perceptual Hash pHash │ │
│   │  • Neo4j Direct Hop Lookup        │ │  • Vietnamese NLP & What-If XAI │ │
│   └─────────────────┬─────────────────┘ └────────────────┬────────────────┘ │
└─────────────────────┼────────────────────────────────────┼──────────────────┘
                      ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       TẦNG LƯU TRỮ KÉP (HYBRID DATA LAYER)                  │
│   [PostgreSQL 16: 17 Thực thể 3NF]     [Neo4j 5.18: Đồ thị liên kết thực thể]│
│   (Users, Devices, Disputes, Audits)   (Phone, BankAccount, Reports, Edges) │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **Nhánh nhanh (Fast-Path):** Phục vụ các truy vấn yêu cầu phản hồi tức thời dưới 100 ms từ dịch vụ `CallScreeningService` của Android, xác định nhanh tình trạng của số điện thoại gọi đến.
2. **Nhánh phân tích sâu (Deep-Path):** Phục vụ thẩm định đa kênh các bài đăng nghi vấn trên Web, kết hợp bóc tách mã VietQR, so khớp mã băm ảnh `pHash`, phân tích đòn tâm lý bằng xử lý ngôn ngữ tự nhiên và truy vấn đường đi ngắn nhất trên đồ thị Neo4j.

---

## 3. Tính năng cốt lõi

### 3.1. Giám sát cuộc gọi lạ thời gian thực trên Android Native
- Tích hợp trực tiếp `CallScreeningService` của hệ điều hành Android, tự động chặn và hiển thị màn hình cảnh báo đỏ đối với các cuộc gọi có điểm rủi ro cao trước khi chuông điện thoại reo.
- Ứng dụng `NotificationListenerService` quét an toàn các chuỗi ký tự khớp mẫu số tài khoản hoặc số điện thoại trong thanh thông báo của Zalo, Messenger, SMS mà không xâm phạm quyền riêng tư của người dùng.

### 3.2. Cơ chế cảnh báo khẩn cấp SOS gia đình
- Thiết lập liên kết tài khoản giữa người cần bảo hộ (người cao tuổi) và người giám hộ (con cái, người thân).
- Khi phát hiện cuộc gọi lừa đảo nguy hiểm kéo dài trên 10 giây hoặc khi người dùng bấm nút SOS, hệ thống lập tức phát cảnh báo đẩy ưu tiên cao qua Firebase Cloud Messaging (FCM) tới người giám hộ với thời gian phản hồi dưới 1 giây.

### 3.3. Thẩm định đa phương thức & Giải mã VietQR
- **Bóc tách chuẩn Napas EMVCo:** Tự động giải mã chuỗi mã QR `000201...` thành các trường dữ liệu định danh: Mã ngân hàng (BIN), Số tài khoản đích, Số tiền và Nội dung thanh toán.
- **Mã băm tri giác 64-bit (`pHash`):** So khớp khoảng cách Hamming ($d \;\le\; 10$) đối với hình ảnh phòng trọ hoặc bảng tuyển dụng tải lên, phát hiện hành vi sử dụng lại kho ảnh căn hộ lừa đảo.
- **Mô phỏng kịch bản giả định What-If:** Ứng dụng mô hình trí tuệ nhân tạo diễn giải minh bạch các bước tiếp theo của kẻ gian nhằm giải thích trực quan nguy cơ tiềm ẩn cho người dùng.

### 3.4. Bảng điều khiển phân tích đồ thị liên kết (Forensic Canvas)
- Giao diện trực quan hóa trên nền Next.js và thư viện Cytoscape.js.
- Cho phép điều tra viên và quản trị viên quan sát cấu trúc mạng lưới tội phạm, các cụm tài khoản luân chuyển tiền và vết liên kết giữa các số điện thoại rác dùng chung thiết bị.

---

## 4. Mô hình tính điểm tín nhiệm

Hệ thống tính toán **Điểm tín nhiệm (Credit Score — $CS$)** chuẩn hóa từ $0.0$ đến $100.0$ dựa trên 4 thành phần trọng số độc lập:

$$P = w_g \cdot S_g + w_p \cdot S_p + w_s \cdot S_s + w_i \cdot S_i$$

$$CS = \max\left(0.0, 100.0 - \min(100.0, P)\right)$$

Trong đó:
- $w_g = 0.40$ (Điểm phạt liên kết đồ thị Neo4j $S_g$, xác định theo khoảng cách ngắn nhất $k \le 3$).
- $w_p = 0.25$ (Điểm phạt đòn thao túng tâm lý NLP $S_p$: tạo áp lực thời gian, đe dọa, mồi chài).
- $w_s = 0.20$ (Điểm phạt lịch sử báo cáo cộng đồng $S_s$).
- $w_i = 0.15$ (Điểm phạt trùng lặp hình ảnh băm tri giác $S_i$).

| Điểm tín nhiệm ($CS$) | Phân loại rủi ro | Nhãn hiển thị | Hành động hệ thống |
| :---: | :---: | :---: | :--- |
| **80.0 – 100.0** | **SAFE** | 🟢 An toàn | Cho phép hoạt động bình thường, không phát hiện dấu hiệu rủi ro. |
| **50.0 – 79.9** | **CAUTION** | 🟡 Thận trọng | Hiển thị biểu ngữ nhắc nhở kiểm tra danh tính đối phương trước khi chuyển tiền. |
| **25.0 – 49.9** | **HIGH_RISK** | 🟠 Nguy cơ cao | Hiển thị cảnh báo trực quan đậm nét, yêu cầu xác nhận 2 bước khi thao tác. |
| **0.0 – 24.9** | **CRITICAL** | 🔴 Cực kỳ nguy hiểm | Chặn cuộc gọi trước chuông; tự động kích hoạt giao thức cảnh báo SOS gia đình. |

---

## 5. Danh mục công nghệ sử dụng

| Phân hệ | Công nghệ | Vai trò kỹ thuật |
| :--- | :--- | :--- |
| **Ứng dụng Di động** | Android Native (Kotlin), Jetpack Compose | Giám sát cuộc gọi ngầm, lắng nghe thông báo, giao diện cảnh báo SOS 1-chạm |
| **Giao diện Web** | Next.js 14, React, Tailwind CSS, Cytoscape.js | Bảng điều khiển tra cứu, trực quan hóa đồ thị liên kết thực thể, duyệt khiếu nại |
| **Máy chủ Dịch vụ** | FastAPI (Python 3.11, AsyncIO), Pydantic v2 | Xử lý logic nghiệp vụ, định tuyến API, tính điểm tín nhiệm bất đồng bộ |
| **Cơ sở dữ liệu Đồ thị** | Neo4j Community 5.18, Cypher Query Language | Mô hình hóa đồ thị thực thể (`PhoneNumber`, `BankAccount`, `ScamReport`) |
| **Cơ sở dữ liệu Quan hệ** | PostgreSQL 16, SQLAlchemy ORM | Quản lý người dùng, thiết bị, nhật ký SOS, hồ sơ báo cáo và kiểm toán |
| **Tự động hóa & Kiểm thử** | Docker Compose, GitHub Actions, Pytest | Đóng gói môi trường container, tự động hóa quy trình kiểm thử liên tục (CI) |

---

## 6. Cấu trúc mã nguồn

```text
antiscam-system/
├── .github/workflows/    # Kịch bản tự động hóa kiểm thử liên tục (CI Pipeline)
├── backend/              # Mã nguồn dịch vụ máy chủ FastAPI
│   ├── app/
│   │   ├── api/v1/       # Bộ định tuyến các endpoints (verify, auth, reports)
│   │   ├── core/         # Cấu hình tập trung hệ thống (config.py đọc từ .env)
│   │   ├── schemas/      # Định nghĩa cấu trúc dữ liệu Pydantic v2 (Data Contracts)
│   │   ├── services/     # Các dịch vụ lõi (scoring, vision, nlp, graph, verification)
│   │   └── main.py       # Điểm khởi động ứng dụng và Middleware đo đạc độ trễ
│   ├── init-db/          # Script khởi tạo 17 bảng quan hệ PostgreSQL (01-init.sql)
│   ├── tests/            # Bộ kiểm thử tự động (25 unit & integration tests)
│   ├── Dockerfile        # Đóng gói container môi trường backend
│   └── requirements.txt  # Danh mục các gói thư viện Python chuẩn hóa
├── web/                  # Mã nguồn ứng dụng Next.js 14 và Cytoscape Graph Canvas
├── mobile/               # Mã nguồn ứng dụng Android Native Kotlin
├── docs/                 # Hồ sơ tài liệu kỹ thuật hoàn chỉnh (SRS, SDD, ERD, RM, Contract)
├── scripts/              # Tiện ích nạp dữ liệu mẫu đồ thị (Seed Data)
└── docker-compose.yml    # Điều phối toàn bộ cụm dịch vụ (FastAPI + PostgreSQL + Neo4j)
```

---

## 7. Hướng dẫn cài đặt & Chạy thử

### Yêu cầu tiên quyết:
- Docker Engine 24.0+ và Docker Compose v2.
- Python 3.11+ (nếu chạy kiểm thử cục bộ).

### 7.1. Khởi chạy cụm dịch vụ bằng Docker
```bash
# 1. Sao chép biến môi trường mẫu
cp .env.example .env

# 2. Khởi chạy toàn bộ hạ tầng (PostgreSQL 16, Neo4j 5.18, FastAPI Backend)
docker compose up -d

# 3. Nạp dữ liệu mẫu ban đầu (Seed Data)
docker compose exec backend python scripts/seed_data.py
```

### 7.2. Các cổng dịch vụ mặc định:
- **Tài liệu API Swagger (OpenAPI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Cơ sở dữ liệu đồ thị Neo4j Console:** [http://localhost:7474](http://localhost:7474) *(Tài khoản: `neo4j` / Mật khẩu: `antiscam_neo4j_pass`)*
- **Giao diện Web Client:** [http://localhost:3000](http://localhost:3000)

### 7.3. Thực thi bộ kiểm thử tự động:
```bash
# Chạy toàn bộ 25 bài kiểm thử đơn vị và tích hợp:
python -m pytest backend/tests/ -v
```

---

## 8. Danh mục tài liệu kỹ thuật

Toàn bộ tài liệu được biên soạn đồng bộ theo chuẩn học thuật của Bộ môn Công nghệ Phần mềm — FIT, HCMUS:

| Tài liệu | Nội dung chi tiết |
| :--- | :--- |
| 📑 [Báo cáo Phân tích Yêu cầu](docs/ANALYSIS.md) | Báo cáo chi tiết theo cấu trúc phân tích nghiệp vụ, ca sử dụng và ràng buộc |
| 📋 [Đề cương Đề tài (Proposal)](docs/PROPOSAL.md) | Khảo sát thực trạng, giải pháp đề xuất, kế hoạch nhân sự và ngân sách |
| 🗄️ [Thiết kế Cơ sở Dữ liệu](docs/DATABASE_SCHEMA.md) | Kiến trúc lưu trữ kép, đặc tả 17 thực thể quan hệ 3NF và Ontology đồ thị Neo4j |
| 🔌 [Đặc tả Hợp đồng API](docs/API_CONTRACT.md) | Hợp đồng giao tiếp dữ liệu chuẩn RESTful JSON giữa Backend, Web và Mobile |
| 🌿 [Quy chuẩn Git & Nhịp làm việc](docs/GIT_WORKFLOW.md) | Chiến lược phân nhánh GitFlow rút gọn và quy ước Conventional Commits |
| 📅 [Kế hoạch Phát triển 12 tuần](docs/WEEKLY_PLAN.md) | Lộ trình phân bổ 5 Sprint theo mô hình Agile/Scrum qua 12 tuần học kỳ |
| 🎯 [Checklist Phân công Sprint 1](docs/TEAM_SPRINT_GUIDE.md) | Bảng giao việc chi tiết, điều kiện tiên quyết và tiêu chuẩn nghiệm thu độc lập |
| 📊 Sơ đồ ERD & Mô hình Quan hệ | Các tệp mô hình chuẩn: [docs/ERD_TongHop_ToanHeThong.xml](docs/ERD_TongHop_ToanHeThong.xml) và [docs/RM_TongHop_ToanHeThong.xml](docs/RM_TongHop_ToanHeThong.xml) |

---

## 9. Thành viên thực hiện

| MSSV | Họ và Tên | Role | Phân hệ phụ trách |
| :---: | :--- | :--- | :--- |
| **24120149** | **Đặng Quang Tiến** | Lead Backend Engineer | Backend Core & Neo4j Engine |
| **24120334** | **Hoàng Khang** | Mobile Engineer | Android CallScreening & Notification Listener |
| **24120397** | **Trương Bảo Nguyên** | Frontend Engineer | Next.js Dashboard & Graph Canvas |
| **24120425** | **Sỉn Thăng Quyền** | DevOps / QA Engineer | Verification Engine & CI/CD Pipeline |

---

## Giấy phép

Mã nguồn dự án được phát hành theo giấy phép mã nguồn mở [MIT License](LICENSE).
