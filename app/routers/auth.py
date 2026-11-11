from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models import User

# Tạo Blueprint quản lý xác thực
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("projects.list_projects"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not full_name or not email or not password:
            flash("Vui lòng nhập đầy đủ thông tin.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Mật khẩu phải có ít nhất 6 ký tự.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp.", "danger")
            return render_template("register.html")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email này đã được đăng ký.", "danger")
            return render_template("register.html")

        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            system_role="USER",
            is_active=True,
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Không thể tạo tài khoản. Vui lòng thử lại.", "danger")
            return render_template("register.html")

        flash("Đăng ký thành công. Hãy đăng nhập.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("projects.list_projects"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        if not email or not password:
            flash("Vui lòng nhập email và mật khẩu.", "danger")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if user is None or not check_password_hash(user.password_hash, password):
            flash("Email hoặc mật khẩu không chính xác.", "danger")
            return render_template("login.html")

        # Kiểm tra tài khoản có bị Admin khóa hay không (yêu cầu PB25)
        if not user.is_active:
            flash("Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Quản trị viên.", "danger")
            return render_template("login.html")

        login_user(user, remember=remember)
        flash(f"Xin chào, {user.full_name}!", "success")

        next_page = request.args.get("next")
        if next_page and next_page.startswith("/") and not next_page.startswith("//"):
            return redirect(next_page)

        # Nếu là Admin, có thể chuyển thẳng đến trang quản trị sau này
        if user.is_admin:
            return redirect(url_for("projects.list_projects"))

        return redirect(url_for("projects.list_projects"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    flash("Đã đăng xuất thành công.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Xem và cập nhật hồ sơ cá nhân (PB03)."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        bio = request.form.get("bio", "").strip()

        if not full_name:
            flash("Họ tên không được để trống.", "danger")
            return render_template("auth/profile.html", user=current_user)

        current_user.full_name = full_name
        current_user.bio = bio

        try:
            db.session.commit()
            flash("Cập nhật hồ sơ thành công.", "success")
        except Exception:
            db.session.rollback()
            flash("Không thể cập nhật hồ sơ. Vui lòng thử lại.", "danger")

    # Tạm thời nếu chưa có template auth/profile.html, có thể dùng sau
    return render_template("auth/profile.html", user=current_user)