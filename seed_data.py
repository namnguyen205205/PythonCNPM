from datetime import date, datetime
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import User, Project, ProjectMember, Task, ProjectDiscussion

app = create_app()

def seed():
    with app.app_context():
        # Xóa và tạo mới bảng
        db.create_all()

        # 1. Tạo tài khoản nếu chưa có
        def get_or_create_user(email, name, role="USER"):
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(
                    email=email,
                    full_name=name,
                    password_hash=generate_password_hash("123456"),
                    system_role=role,
                    is_active=True
                )
                db.session.add(u)
                db.session.flush()
            return u

        admin = get_or_create_user("admin@gmail.com", "Quản trị viên", "ADMIN")
        sv_a = get_or_create_user("sinhvien_a@gmail.com", "Nguyễn Văn A")
        sv_b = get_or_create_user("sinhvien_b@gmail.com", "Trần Thị B")
        sv_c = get_or_create_user("sinhvien_c@gmail.com", "Lê Văn C")

        # 2. Tạo Dự án 1: Đã duyệt (APPROVED)
        p1 = Project.query.filter_by(name="Xây dựng Website Quản lý Nhóm CNPM").first()
        if not p1:
            p1 = Project(
                name="Xây dựng Website Quản lý Nhóm CNPM",
                description="Đồ án học phần Công nghệ phần mềm - Nhóm 3 người",
                due_date=date(2026, 12, 30),
                status="ACTIVE",
                approval_status="APPROVED",
                created_by=sv_a.id,
                reviewed_by=admin.id,
                reviewed_at=datetime.utcnow()
            )
            db.session.add(p1)
            db.session.flush()

            # Thêm thành viên
            db.session.add(ProjectMember(project_id=p1.id, user_id=sv_a.id, role="LEADER"))
            db.session.add(ProjectMember(project_id=p1.id, user_id=sv_b.id, role="MEMBER"))
            db.session.add(ProjectMember(project_id=p1.id, user_id=sv_c.id, role="MEMBER"))

            # Thêm các Task
            t1 = Task(project_id=p1.id, title="Khảo sát yêu cầu và viết Product Backlog", status="DONE", priority="HIGH", assignee_id=sv_a.id)
            t2 = Task(project_id=p1.id, title="Thiết kế CSDL và viết models Flask", status="IN_PROGRESS", priority="HIGH", assignee_id=sv_b.id)
            t3 = Task(project_id=p1.id, title="Thiết kế giao diện Bootstrap và kiểm thử", status="TODO", priority="MEDIUM", assignee_id=sv_c.id)
            db.session.add_all([t1, t2, t3])

            # Thêm Thảo luận
            d1 = ProjectDiscussion(project_id=p1.id, user_id=sv_a.id, content="Chào cả nhóm, mình đã chia các task chính trong đồ án rồi nhé!")
            d2 = ProjectDiscussion(project_id=p1.id, user_id=sv_b.id, content="Ok bạn, phần thiết kế CSDL mình đang làm dở, dự kiến mai xong.")
            db.session.add_all([d1, d2])

        # 3. Tạo Dự án 2: Chờ duyệt (PENDING)
        p2 = Project.query.filter_by(name="Nghiên cứu ứng dụng IoT trong nông nghiệp").first()
        if not p2:
            p2 = Project(
                name="Nghiên cứu ứng dụng IoT trong nông nghiệp",
                description="Đồ án môn Hệ thống nhúng",
                due_date=date(2026, 11, 20),
                status="ACTIVE",
                approval_status="PENDING",
                created_by=sv_b.id
            )
            db.session.add(p2)
            db.session.flush()
            db.session.add(ProjectMember(project_id=p2.id, user_id=sv_b.id, role="LEADER"))

        db.session.commit()
        print(">>> Nap du lieu mau demo thanh cong!")

if __name__ == "__main__":
    seed()
