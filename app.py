import os
from datetime import date, datetime
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)
from flask_sqlalchemy import SQLAlchemy


load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "dev-secret-key",
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///project_manager.db",
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Bạn cần đăng nhập để xem trang này."
login_manager.login_message_category = "warning"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(
        db.String(100),
        nullable=False,
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    due_date = db.Column(
        db.Date,
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        default="ACTIVE",
        nullable=False,
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    memberships = db.relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProjectMember(db.Model):
    __tablename__ = "project_members"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    role = db.Column(
        db.String(20),
        default="MEMBER",
        nullable=False,
    )

    joined_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    project = db.relationship(
        "Project",
        back_populates="memberships",
    )

    user = db.relationship("User")

    __table_args__ = (
        db.UniqueConstraint(
            "project_id",
            "user_id",
            name="uq_project_member",
        ),
    )


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        full_name = request.form.get(
            "full_name",
            "",
        ).strip()

        email = request.form.get(
            "email",
            "",
        ).strip().lower()

        password = request.form.get(
            "password",
            "",
        )

        confirm_password = request.form.get(
            "confirm_password",
            "",
        )

        if not full_name or not email or not password:
            flash(
                "Vui lòng nhập đầy đủ thông tin.",
                "danger",
            )
            return render_template("register.html")

        if len(password) < 6:
            flash(
                "Mật khẩu phải có ít nhất 6 ký tự.",
                "danger",
            )
            return render_template("register.html")

        if password != confirm_password:
            flash(
                "Mật khẩu xác nhận không khớp.",
                "danger",
            )
            return render_template("register.html")

        existing_user = User.query.filter_by(
            email=email,
        ).first()

        if existing_user:
            flash(
                "Email này đã được đăng ký.",
                "danger",
            )
            return render_template("register.html")

        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception:
            db.session.rollback()

            flash(
                "Không thể tạo tài khoản. Vui lòng thử lại.",
                "danger",
            )
            return render_template("register.html")

        flash(
            "Đăng ký thành công. Hãy đăng nhập.",
            "success",
        )

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get(
            "email",
            "",
        ).strip().lower()

        password = request.form.get(
            "password",
            "",
        )

        remember = request.form.get("remember") == "on"

        if not email or not password:
            flash(
                "Vui lòng nhập email và mật khẩu.",
                "danger",
            )
            return render_template("login.html")

        user = User.query.filter_by(
            email=email,
        ).first()

        if user is None or not check_password_hash(
            user.password_hash,
            password,
        ):
            flash(
                "Email hoặc mật khẩu không chính xác.",
                "danger",
            )
            return render_template("login.html")

        login_user(
            user,
            remember=remember,
        )

        flash(
            "Đăng nhập thành công.",
            "success",
        )

        next_page = request.args.get("next")

        if (
            next_page
            and next_page.startswith("/")
            and not next_page.startswith("//")
        ):
            return redirect(next_page)

        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/projects")
@login_required
def projects():
    memberships = (
        ProjectMember.query
        .filter_by(user_id=current_user.id)
        .join(Project)
        .order_by(Project.created_at.desc())
        .all()
    )

    return render_template(
        "projects.html",
        memberships=memberships,
    )
@app.route("/projects/create", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        name = request.form.get(
            "name",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        due_date_text = request.form.get(
            "due_date",
            "",
        ).strip()

        if not name:
            flash(
                "Tên dự án là bắt buộc.",
                "danger",
            )
            return render_template("create_project.html")

        if len(name) > 150:
            flash(
                "Tên dự án không được dài quá 150 ký tự.",
                "danger",
            )
            return render_template("create_project.html")

        due_date = None

        if due_date_text:
            try:
                due_date = date.fromisoformat(due_date_text)
            except ValueError:
                flash(
                    "Hạn dự kiến không hợp lệ.",
                    "danger",
                )
                return render_template("create_project.html")

        new_project = Project(
            name=name,
            description=description,
            due_date=due_date,
            status="ACTIVE",
            created_by=current_user.id,
        )

        try:
            db.session.add(new_project)

            # Gửi lệnh INSERT tạm thời để lấy ID dự án.
            db.session.flush()

            leader_membership = ProjectMember(
                project_id=new_project.id,
                user_id=current_user.id,
                role="LEADER",
            )

            db.session.add(leader_membership)
            db.session.commit()

        except Exception:
            db.session.rollback()

            flash(
                "Không thể tạo dự án. Vui lòng thử lại.",
                "danger",
            )
            return render_template("create_project.html")

        flash(
            "Tạo dự án thành công.",
            "success",
        )

        return redirect(url_for("projects"))

    return render_template("create_project.html")
@app.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id):
    membership = ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=current_user.id,
    ).first()

    if membership is None:
        flash(
            "Bạn không có quyền truy cập dự án này.",
            "danger",
        )
        return redirect(url_for("projects"))

    return render_template(
        "project_detail.html",
        project=membership.project,
        membership=membership,
    )
@app.route(
    "/projects/<int:project_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_project(project_id):
    membership = ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=current_user.id,
    ).first()

    if membership is None:
        flash(
            "Bạn không có quyền truy cập dự án này.",
            "danger",
        )
        return redirect(url_for("projects"))

    if membership.role != "LEADER":
        flash(
            "Chỉ trưởng nhóm được sửa dự án.",
            "danger",
        )
        return redirect(
            url_for(
                "project_detail",
                project_id=project_id,
            )
        )

    project = membership.project

    if request.method == "POST":
        name = request.form.get(
            "name",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        due_date_text = request.form.get(
            "due_date",
            "",
        ).strip()

        if not name:
            flash(
                "Tên dự án là bắt buộc.",
                "danger",
            )
            return render_template(
                "edit_project.html",
                project=project,
            )

        if len(name) > 150:
            flash(
                "Tên dự án không được dài quá 150 ký tự.",
                "danger",
            )
            return render_template(
                "edit_project.html",
                project=project,
            )

        due_date = None

        if due_date_text:
            try:
                due_date = date.fromisoformat(due_date_text)
            except ValueError:
                flash(
                    "Hạn dự kiến không hợp lệ.",
                    "danger",
                )
                return render_template(
                    "edit_project.html",
                    project=project,
                )

        project.name = name
        project.description = description
        project.due_date = due_date

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

            flash(
                "Không thể cập nhật dự án.",
                "danger",
            )
            return render_template(
                "edit_project.html",
                project=project,
            )

        flash(
            "Cập nhật dự án thành công.",
            "success",
        )

        return redirect(
            url_for(
                "project_detail",
                project_id=project.id,
            )
        )

    return render_template(
        "edit_project.html",
        project=project,
    )
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("projects"))

    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
