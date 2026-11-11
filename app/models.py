from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, nullable=True)  # Há»“ sÆ¡ cĂ¡ nhĂ¢n

    # NĂ¢ng cáº¥p cho Admin:
    # Vai trĂ² há»‡ thá»‘ng: "USER" hoáº·c "ADMIN"
    system_role = db.Column(db.String(20), default="USER", nullable=False)
    # Tráº¡ng thĂ¡i tĂ i khoáº£n: True = Hoáº¡t Ä‘á»™ng, False = Bá»‹ khĂ³a
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Thuá»™c tĂ­nh tiá»‡n Ă­ch Ä‘á»ƒ kiá»ƒm tra nhanh quyá»n Admin
    @property
    def is_admin(self):
        return self.system_role == "ADMIN"

    def __repr__(self):
        return f"<User {self.email} ({self.system_role})>"


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="ACTIVE", nullable=False)  # ACTIVE / ARCHIVED
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # NĂ¢ng cáº¥p quy trĂ¬nh duyá»‡t dá»± Ă¡n cho Admin:
    # Tráº¡ng thĂ¡i duyá»‡t: PENDING (Chá» duyá»‡t) / APPROVED (ÄĂ£ duyá»‡t) / REJECTED (Bá»‹ tá»« chá»‘i)
    approval_status = db.Column(db.String(20), default="PENDING", nullable=False)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reject_reason = db.Column(db.Text, nullable=True)

    # Quan há»‡
    creator = db.relationship("User", foreign_keys=[created_by], backref="created_projects")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by], backref="reviewed_projects")
    memberships = db.relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Project {self.name} [{self.approval_status}]>"
    @property
    def progress_percentage(self):
        """TĂ­nh % tiáº¿n Ä‘á»™ hoĂ n thĂ nh cá»§a dá»± Ă¡n (PB16)."""
        total = len(self.tasks)
        if total == 0:
            return 0
        done_count = sum(1 for t in self.tasks if t.status == "DONE")
        return round((done_count / total) * 100, 1)

class ProjectMember(db.Model):
    __tablename__ = "project_members"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(20), default="MEMBER", nullable=False)  # LEADER / MEMBER
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    project = db.relationship("Project", back_populates="memberships")
    user = db.relationship("User", backref="project_memberships")

    __table_args__ = (
        db.UniqueConstraint("project_id", "user_id", name="uq_project_member"),
    )

    def __repr__(self):
        return f"<ProjectMember user={self.user_id} project={self.project_id} role={self.role}>"

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # NgÆ°á»i phá»¥ trĂ¡ch

    # Tráº¡ng thĂ¡i: TODO (ChÆ°a lĂ m) / IN_PROGRESS (Äang lĂ m) / DONE (HoĂ n thĂ nh)
    status = db.Column(db.String(20), default="TODO", nullable=False)
    # Má»©c Æ°u tiĂªn: LOW (Tháº¥p) / MEDIUM (Trung bĂ¬nh) / HIGH (Cao)
    priority = db.Column(db.String(20), default="MEDIUM", nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Quan há»‡
    project = db.relationship("Project", backref=db.backref("tasks", cascade="all, delete-orphan"))
    assignee = db.relationship("User", backref="assigned_tasks")

    def __repr__(self):
        return f"<Task {self.title} [{self.status}]>"
class ProjectDiscussion(db.Model):
    __tablename__ = "project_discussions"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Quan há»‡
    project = db.relationship("Project", backref=db.backref("discussions", cascade="all, delete-orphan", order_by="ProjectDiscussion.created_at.asc()"))
    author = db.relationship("User", backref="discussions")

    def __repr__(self):
        return f"<Discussion by {self.author.full_name} in Project {self.project_id}>"
# HĂ m load user cho Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
