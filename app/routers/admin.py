from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Project
from app.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
@login_required
@admin_required
def require_admin():
    """Tất cả các route trong admin_bp đều phải là Admin."""
    pass


@admin_bp.route("/dashboard")
def dashboard():
    """Trang tổng quan thống kê hệ thống (PB27)."""
    total_users = User.query.filter_by(system_role="USER").count()
    active_users = User.query.filter_by(system_role="USER", is_active=True).count()
    locked_users = total_users - active_users

    total_projects = Project.query.count()
    pending_projects = Project.query.filter_by(approval_status="PENDING").count()
    approved_projects = Project.query.filter_by(approval_status="APPROVED").count()
    rejected_projects = Project.query.filter_by(approval_status="REJECTED").count()

    stats = {
        "total_users": total_users,
        "active_users": active_users,
        "locked_users": locked_users,
        "total_projects": total_projects,
        "pending_projects": pending_projects,
        "approved_projects": approved_projects,
        "rejected_projects": rejected_projects,
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/approvals")
def project_approvals():
    """Trang danh sách dự án chờ duyệt (PB26)."""
    pending_list = Project.query.filter_by(approval_status="PENDING").order_by(Project.created_at.desc()).all()
    history_list = Project.query.filter(Project.approval_status != "PENDING").order_by(Project.reviewed_at.desc()).limit(20).all()
    return render_template("admin/project_approvals.html", pending_list=pending_list, history_list=history_list)


@admin_bp.route("/projects/<int:project_id>/approve", methods=["POST"])
def approve_project(project_id):
    """Xử lý phê duyệt dự án (PB26)."""
    project = Project.query.get_or_404(project_id)
    project.approval_status = "APPROVED"
    project.reviewed_by = current_user.id
    project.reviewed_at = datetime.utcnow()
    project.reject_reason = None

    db.session.commit()
    flash(f"Đã phê duyệt dự án '{project.name}' thành công!", "success")
    return redirect(url_for("admin.project_approvals"))


@admin_bp.route("/projects/<int:project_id>/reject", methods=["POST"])
def reject_project(project_id):
    """Xử lý từ chối dự án có lý do (PB26)."""
    project = Project.query.get_or_404(project_id)
    reason = request.form.get("reject_reason", "").strip()

    if not reason:
        flash("Vui lòng nhập lý do từ chối dự án.", "danger")
        return redirect(url_for("admin.project_approvals"))

    project.approval_status = "REJECTED"
    project.reviewed_by = current_user.id
    project.reviewed_at = datetime.utcnow()
    project.reject_reason = reason

    db.session.commit()
    flash(f"Đã từ chối dự án '{project.name}'.", "warning")
    return redirect(url_for("admin.project_approvals"))


@admin_bp.route("/users")
def users_list():
    """Quản lý danh sách người dùng (PB25)."""
    search = request.args.get("q", "").strip()
    query = User.query.filter(User.id != current_user.id)  # Không hiện chính mình

    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users, search=search)


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
def toggle_user_status(user_id):
    """Khóa / Mở khóa tài khoản người dùng (PB25)."""
    user = User.query.get_or_404(user_id)

    # Chặn không cho tự khóa chính mình
    if user.id == current_user.id:
        flash("Bạn không thể tự khóa tài khoản của chính mình!", "danger")
        return redirect(url_for("admin.users_list"))

    user.is_active = not user.is_active
    db.session.commit()

    trang_thai = "Mở khóa" if user.is_active else "Khóa"
    flash(f"Đã {trang_thai} tài khoản {user.email} thành công.", "info")
    return redirect(url_for("admin.users_list"))