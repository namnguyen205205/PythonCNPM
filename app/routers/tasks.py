from datetime import date
from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Project, ProjectMember, Task, User

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("/projects/<int:project_id>/create", methods=["POST"])
@login_required
def create_task(project_id):
    """Tạo công việc mới trong dự án (PB10, PB11)."""
    project = Project.query.get_or_404(project_id)

    # 1. Kiểm tra quyền: Chỉ Trưởng nhóm mới được tạo task
    membership = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not membership or membership.role != "LEADER":
        flash("Chỉ trưởng nhóm mới có quyền tạo công việc.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    # 2. Quy tắc nghiệp vụ: Dự án phải ĐƯỢC DUYỆT mới cho tạo task (TC18)
    if project.approval_status != "APPROVED":
        flash("Dự án chưa được phê duyệt, không thể tạo công việc.", "warning")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "MEDIUM").strip()
    due_date_text = request.form.get("due_date", "").strip()
    assignee_id_raw = request.form.get("assignee_id", "").strip()

    if not title:
        flash("Tiêu đề công việc là bắt buộc.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    # Xử lý hạn chót
    due_date = None
    if due_date_text:
        try:
            due_date = date.fromisoformat(due_date_text)
        except ValueError:
            flash("Hạn hoàn thành không hợp lệ.", "danger")
            return redirect(url_for("projects.project_detail", project_id=project_id))

    # Xử lý phân công: Kiểm tra người được giao có thuộc dự án không (TC07)
    assignee_id = None
    if assignee_id_raw:
        assignee_id = int(assignee_id_raw)
        is_member = ProjectMember.query.filter_by(project_id=project_id, user_id=assignee_id).first()
        if not is_member:
            flash("Không thể phân công cho người ngoài dự án.", "danger")
            return redirect(url_for("projects.project_detail", project_id=project_id))

    new_task = Task(
        project_id=project_id,
        title=title,
        description=description,
        priority=priority,
        status="TODO",
        due_date=due_date,
        assignee_id=assignee_id
    )

    db.session.add(new_task)
    db.session.commit()
    flash(f"Đã tạo công việc '{title}' thành công!", "success")
    return redirect(url_for("projects.project_detail", project_id=project_id))


@tasks_bp.route("/<int:task_id>/update-status", methods=["POST"])
@login_required
def update_status(task_id):
    """Cập nhật trạng thái công việc (PB14)."""
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id

    # Kiểm tra xem người dùng có thuộc dự án này không (TC09)
    membership = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not membership and not current_user.is_admin:
        flash("Bạn không thuộc dự án này nên không thể cập nhật công việc.", "danger")
        return redirect(url_for("projects.list_projects"))

    # Quyền đổi trạng thái: Phải là Trưởng nhóm HOẶC là người được giao việc đó (TC08)
    if membership.role != "LEADER" and task.assignee_id != current_user.id:
        flash("Bạn chỉ có quyền cập nhật công việc được giao cho chính mình.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    new_status = request.form.get("status", "").strip()
    if new_status in ["TODO", "IN_PROGRESS", "DONE"]:
        task.status = new_status
        db.session.commit()
        flash("Cập nhật trạng thái công việc thành công!", "success")
    else:
        flash("Trạng thái không hợp lệ.", "danger")

    return redirect(url_for("projects.project_detail", project_id=project_id))


@tasks_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    """Xóa công việc (PB12 - chỉ Trưởng nhóm)."""
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id

    membership = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not membership or membership.role != "LEADER":
        flash("Chỉ trưởng nhóm mới có quyền xóa công việc.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    db.session.delete(task)
    db.session.commit()
    flash("Đã xóa công việc thành công.", "info")
    return redirect(url_for("projects.project_detail", project_id=project_id))