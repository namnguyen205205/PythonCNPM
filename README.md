# 🎓 HỆ THỐNG QUẢN LÝ DỰ ÁN NHÓM CHO SINH VIÊN
> **Học phần:** Công nghệ Phần mềm  
> **Đề tài số 11:** Xây dựng hệ thống quản lý dự án nhóm cho sinh viên  
> **Nhóm thực hiện:** Nhóm 3  

---

## 📌 1. Giới thiệu đề tài
Hệ thống hỗ trợ sinh viên trong các học phần làm việc nhóm lập kế hoạch, phân công nhiệm vụ, theo dõi tiến độ đồ án và trao đổi tập trung trong cùng một không gian làm việc. Hệ thống tích hợp phân hệ **Quản trị viên (Admin)** giúp kiểm soát chất lượng dự án và quản lý tài khoản người dùng trong toàn trường.

### 🌟 Các chức năng chính:
* **Quản lý dự án học tập:** Khởi tạo dự án, thiết lập hạn hoàn thành, phân quyền Trưởng nhóm (`LEADER`) và Thành viên (`MEMBER`).
* **Quản lý thành viên nhóm:** Mời bạn học vào nhóm đồ án bằng email, phân quyền và loại bỏ thành viên.
* **Phân công công việc (Task):** Tạo đầu việc, chỉ định người phụ trách, gắn mức ưu tiên (Cao / TB / Thấp), đặt hạn chót.
* **Theo dõi tiến độ tự động:** Chuyển đổi trạng thái (*Chưa làm / Đang làm / Hoàn thành*), hệ thống tự động tính `% tiến độ hoàn thành` theo thời gian thực.
* **Bảng thảo luận nội bộ:** Trao đổi, nhắn tin theo ngữ cảnh dự án theo dòng thời gian.
* **Phân hệ Quản trị viên (Admin nâng cao):**
  - Dashboard thống kê tổng quan (người dùng, dự án theo trạng thái).
  - Phê duyệt / Từ chối dự án của sinh viên (kèm lý do).
  - Quản lý danh sách sinh viên, Khóa / Mở khóa tài khoản vi phạm.

---

## 🛠️ 2. Công nghệ sử dụng
* **Backend:** Python 3.11, Flask 3.1 (Mô hình Application Factory & Blueprints)
* **Frontend:** HTML5, CSS3, Bootstrap 5.3 (Giao diện tối giản, thanh lịch, chuẩn mực), Bootstrap Icons
* **Cơ sở dữ liệu:** PostgreSQL 16 (Hỗ trợ SQLite chạy thử nghiệm nội bộ)
* **ORM & Quản lý phiên:** Flask-SQLAlchemy, Flask-Login, Flask-Migrate
* **Đóng gói & Triển khai:** Docker, Docker Compose, Gunicorn

---

## 📂 3. Cấu trúc thư mục dự án
```text
student_project_manager/
├── app/
│   ├── __init__.py          # Khởi tạo app & đăng ký 4 Blueprint
│   ├── extensions.py        # Khởi tạo db, login_manager, migrate
│   ├── models.py            # User, Project, ProjectMember, Task, ProjectDiscussion
│   ├── decorators.py        # Decorator @admin_required bảo mật route quản trị
│   ├── routers/
│   │   ├── auth.py          # Xác thực, đăng ký, đăng nhập, hồ sơ
│   │   ├── projects.py      # Dự án & quản lý thành viên nhóm
│   │   ├── tasks.py         # Quản lý công việc & phân công
│   │   └── admin.py         # Dashboard, duyệt dự án, quản lý tài khoản
│   └── templates/           # Giao diện HTML Bootstrap 5
│       ├── base.html
│       ├── projects.html, project_detail.html, ...
│       └── admin/           # dashboard.html, project_approvals.html, users.html
├── Dockerfile               # Cấu hình đóng gói container ứng dụng
├── docker-compose.yml       # Điều phối dịch vụ Web Flask + PostgreSQL 16
├── database.sql             # Script SQL tạo bảng và nạp dữ liệu mẫu
├── seed_data.py             # Script Python nạp dữ liệu demo
├── config.py & run.py       # Cấu hình môi trường & điểm khởi chạy ứng dụng
└── requirements.txt         # Danh sách thư viện Python phụ thuộc
```

---

## 🚀 4. Hướng dẫn cài đặt và khởi chạy dự án

### Cách 1: Chạy bằng Môi trường ảo Python (`venv`) & SQLite (Môi trường phát triển)

Dành cho thành viên phát triển hoặc máy chưa cài Docker:

#### 1. Mở Terminal và di chuyển vào thư mục dự án:
```powershell
cd student_project_manager
```

#### 2. Khởi tạo môi trường ảo Python (`venv`):
```powershell
python -m venv .venv
```

#### 3. Kích hoạt môi trường ảo:
* **Trên Windows PowerShell:**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
  *(Nếu gặp lỗi script policy, chạy lệnh: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` rồi kích hoạt lại)*.
* **Trên Windows Command Prompt (cmd):**
  ```cmd
  .venv\Scripts\activate.bat
  ```
* **Trên macOS / Linux:**
  ```bash
  source .venv/bin/activate
  ```
*(Khi kích hoạt thành công, đầu dòng lệnh sẽ xuất hiện tiền tố `(.venv)`)*.

#### 4. Cài đặt các thư viện cần thiết:
```powershell
pip install -r requirements.txt
```

#### 5. Khởi tạo CSDL và nạp dữ liệu mẫu demo:
```powershell
python seed_data.py
```

#### 6. Khởi chạy máy chủ Web:
```powershell
python run.py
```
👉 Truy cập hệ thống tại: **`http://127.0.0.1:5000`**

---

### Cách 2: Chạy đóng gói bằng Docker Compose & PostgreSQL (Khuyên dùng)

Yêu cầu máy tính đã bật **Docker Desktop**.

#### 1. Khởi chạy toàn bộ hệ thống bằng một lệnh:
```powershell
cd student_project_manager
docker compose up --build -d
```
*Lệnh này sẽ tự động khởi tạo server PostgreSQL 16, tự động nạp toàn bộ bảng và dữ liệu từ file `database.sql`, sau đó khởi chạy web Flask trên máy chủ Gunicorn.*

#### 2. Truy cập hệ thống:
👉 Mở trình duyệt vào: **`http://localhost:5000`**

#### 3. Dừng hệ thống Docker:
```powershell
docker compose down
```

---

## 🔑 5. Tài khoản thử nghiệm (Demo Accounts)
Tất cả tài khoản mẫu có mật khẩu mặc định: **`123456`**

| Vai trò | Email đăng nhập | Họ và tên | Quyền hạn chính |
|---|---|---|---|
| **Quản trị viên** | `admin@gmail.com` | Quản trị viên | Dashboard, Duyệt/Từ chối dự án, Khóa user |
| **Sinh viên (Leader)** | `sinhvien_a@gmail.com` | Nguyễn Văn A | Trưởng nhóm, tạo dự án, phân công việc, chat |
| **Sinh viên (Member)** | `sinhvien_b@gmail.com` | Trần Thị B | Thành viên, cập nhật trạng thái việc `DONE` |
| **Sinh viên (Member)** | `sinhvien_c@gmail.com` | Lê Văn C | Thành viên tham gia nhóm đồ án |

---

## 👥 6. Thành viên nhóm thực hiện
* **Thành viên 1:** [Tên của bạn] - *Trưởng nhóm / Backend Lead & DevOps*
* **Thành viên 2:** [Tên thành viên 2] - *Frontend Developer & Báo cáo*
* **Thành viên 3:** [Tên thành viên 3] - *Database Administrator & Tester*
