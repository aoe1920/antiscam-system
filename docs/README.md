# THƯ MỤC TÀI LIỆU KỸ THUẬT DỰ ÁN SMARTGUARD

> **Đề tài:** Hệ thống kiểm chứng và cảnh báo lừa đảo trực tuyến  
> **Bộ môn:** Công nghệ Phần mềm — Khoa Công nghệ Thông tin, Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM  
> **Lớp học phần:** 24_31 • **Nhóm:** 03  

Thư mục này chứa toàn bộ hồ sơ thiết kế, đặc tả kỹ thuật và tài liệu quản lý dự án được biên soạn chuẩn mực theo quy trình kỹ nghệ phần mềm.

---

## 1. Bản Đồ Tài Liệu Kỹ Thuật (Documentation Sitemap)

```
docs/
├── README.md                   # Trang mục lục trung tâm (Tài liệu này)
├── PROPOSAL.md                 # Đề cương đề tài, khảo sát bài toán và dự toán
├── ANALYSIS.md                 # Báo cáo Phân tích Yêu cầu Phần mềm (SRS)
├── DATABASE_SCHEMA.md          # Đặc tả Cơ sở dữ liệu Kép (PostgreSQL 3NF + Neo4j Graph)
├── API_CONTRACT.md             # Hợp đồng giao tiếp dữ liệu chuẩn RESTful API
├── GIT_WORKFLOW.md             # Quy chuẩn phân nhánh GitFlow và Conventional Commits
├── WEEKLY_PLAN.md              # Lộ trình 12 tuần (5 Sprints) theo mô hình Agile/Scrum
├── TEAM_SPRINT_GUIDE.md        # Kế hoạch chi tiết và Checklist nghiệm thu Sprint 1
├── ERD_TongHop_ToanHeThong.xml # Sơ đồ Thực thể - Mối quan hệ (ERD - Draw.io XML)
├── RM_TongHop_ToanHeThong.xml  # Sơ đồ Mô hình Quan hệ (Relational Model - Draw.io XML)
└── img/                        # Thư mục hình ảnh, sơ đồ kiến trúc và wireframe giao diện
```

---

## 2. Chi Tiết Danh Mục Hồ Sơ & Vai Trò

### 2.1. Phân tích Yêu cầu & Đặc tả Hệ thống
- **[PROPOSAL.md](PROPOSAL.md):** Văn kiện đề xuất đề tài được thông qua ở đầu kỳ, bao gồm bối cảnh thực trạng, đối tượng thụ hưởng, giải pháp đa phương thức, kế hoạch phân bổ nguồn lực và bảng thuật ngữ chuyên ngành.
- **[ANALYSIS.md](ANALYSIS.md):** Báo cáo phân tích yêu cầu phần mềm toàn diện (Software Requirements Specification - SRS):
  - Phân tích 6 nhóm tác nhân ngoài (Stakeholders) và Context Diagram.
  - 27 yêu cầu chức năng (User Stories - Requirements - Acceptance Criteria) phân loại theo 6 nhóm nghiệp vụ chính: FR-0 (Tài khoản), FR-1 (Giám sát di động), FR-2 (Thẩm định bài đăng), FR-3 (Lõi đồ thị), FR-4 (Báo cáo cộng đồng), FR-5 (Khiếu nại và Quản trị).
  - Đặc tả Use Case chi tiết (U001 đến U012) kèm sơ đồ hoạt động và luồng ngoại lệ.

### 2.2. Kiến Trúc Dữ Liệu & Mô Hình Hóa
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md):** Tài liệu thiết kế cơ sở dữ liệu kép:
  - *PostgreSQL 16:* Chuẩn hóa 17 bảng đạt tối thiểu dạng chuẩn 3 (3NF), chia thành 4 phân hệ (Người dùng, Ngân hàng, Báo cáo lừa đảo, Cấu hình kiểm toán).
  - *Neo4j 5.18:* Mô hình hóa đồ thị tri thức (Property Graph Model) định nghĩa các nút (:User, :PhoneNumber, :BankAccount, :ScamReport) và các quan hệ (:LINKED_TO, :TRANSFERRED_TO, :REPORTED_FOR).
- **[ERD_TongHop_ToanHeThong.xml](ERD_TongHop_ToanHeThong.xml):** Sơ đồ ERD tổng thể định dạng mở (Draw.io), biểu diễn trực quan các thực thể và ràng buộc toàn vẹn.
- **[RM_TongHop_ToanHeThong.xml](RM_TongHop_ToanHeThong.xml):** Sơ đồ Mô hình Quan hệ (Relational Model) thể hiện khóa chính (PK), khóa ngoại (FK) và liên kết giữa 17 bảng.

### 2.3. Hợp Đồng Giao Diện & Tích Hợp
- **[API_CONTRACT.md](API_CONTRACT.md):** Giao ước dữ liệu giữa Backend (FastAPI), Web Client (Next.js) và Mobile App (Android Kotlin):
  - Chuẩn hóa cấu trúc JSON trả về (`success`, `data`, `message`, `error`).
  - Đặc tả chi tiết từng endpoint: Phương thức HTTP, Headers, Request Body mẫu, Response Codes (200, 400, 401, 403, 404, 500).
  - Giúp các thành viên xây dựng tính năng độc lập thông qua Mock Data mà không bị nghẽn tiến độ.

### 2.4. Quản Lý Dự Án & Quy Trình Kỹ Thuật
- **[GIT_WORKFLOW.md](GIT_WORKFLOW.md):** Quy định kỷ luật làm việc bằng Git: Mô hình phân nhánh GitFlow rút gọn (`main`, `develop`, `feature/*`, `fix/*`), chuẩn đặt tên commit theo Conventional Commits và quy trình Code Review bắt buộc trước khi merge.
- **[WEEKLY_PLAN.md](WEEKLY_PLAN.md):** Kế hoạch chi tiết phân bổ 12 tuần học kỳ thành 5 Sprint (Sprint 0: Khảo sát; Sprint 1: MVP 1; Sprint 2: Đồ thị & SOS; Sprint 3: Trực quan hóa & Test; Sprint 4: Đóng gói & Nghiệm thu).
- **[TEAM_SPRINT_GUIDE.md](TEAM_SPRINT_GUIDE.md):** Bản kế hoạch hành động cụ thể cho từng cá nhân trong nhóm, liệt kê checklist công việc độc lập cho 4 thành viên trong Sprint 1.

---

## 3. Quy Ước Cập Nhật & Đóng Góp Tài Liệu
1. Mọi thay đổi về cấu trúc API bắt buộc phải cập nhật trước tại `API_CONTRACT.md` và thông báo cho toàn đội ngũ trước khi sửa đổi mã nguồn.
2. Mọi thay đổi về cấu trúc cơ sở dữ liệu phải được đồng bộ song song giữa `DATABASE_SCHEMA.md` và file khởi tạo `backend/init-db/01-init.sql`.
3. Toàn bộ tài liệu phải tuân thủ nghiêm ngặt văn phong học thuật, sử dụng thuật ngữ tiếng Việt chuẩn hóa của ngành Công nghệ Phần mềm.
