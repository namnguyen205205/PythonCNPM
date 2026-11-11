from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Project, ProjectMember, User, ProjectDiscussion

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/")
@login_required
def list_projects():
    """Xem danh sách dự án tham gia (PB07)."""
    memberships = (
        ProjectMember.query.filter_by(user_id=current_user.id)
        .join(Project)
        .order_by(Project.created_at.desc())
        .all()
    )
    return render_template("projects.html", memberships=memberships)


@projects_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_project():
    """Tạo dự án mới (PB05) - mặc định ở trạng thái PENDING chờ Admin duyệt."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        due_date_text = request.form.get("due_date", "").strip()

        if not name:
            flash("Tên dự án là bắt buộc.", "danger")
            return render_template("create_project.html")

        if len(name) > 150:
            flash("Tên dự án không được dài quá 150 ký tự.", "danger")
            return render_template("create_project.html")

        due_date = None
        if due_date_text:
            try:
                due_date = date.fromisoformat(due_date_text)
            except ValueError:
                flash("Hạn dự kiến không hợp lệ.", "danger")
                return render_template("create_project.html")

        # Dự án mới tạo mặc định: approval_status="PENDING"
        new_project = Project(
            name=name,
            description=description,
            due_date=due_date,
            status="ACTIVE",
            approval_status="PENDING",
            created_by=current_user.id,
        )

        try:
            db.session.add(new_project)
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
            flash("Không thể tạo dự án. Vui lòng thử lại.", "danger")
            return render_template("create_project.html")

        flash("Tạo dự án thành công! Dự án đang ở trạng thái Chờ duyệt bởi Quản trị viên.", "info")
        return redirect(url_for("projects.list_projects"))

    return render_template("create_project.html")


@projects_bp.route("/<int:project_id>")
@login_required
def project_detail(project_id):
    """Xem chi tiết dự án (PB07)."""
    # Nếu là Admin hệ thống thì có quyền xem mọi dự án
    if current_user.is_admin:
        project = Project.query.get_or_404(project_id)
        membership = ProjectMember.query.filter_by(
            project_id=project_id, user_id=current_user.id
        ).first()
        return render_template("project_detail.html", project=project, membership=membership)

    membership = ProjectMember.query.filter_by(
        project_id=project_id, user_id=current_user.id
    ).first()

    if membership is None:
        flash("Bạn không có quyền truy cập dự án này.", "danger")
        return redirect(url_for("projects.list_projects"))

    return render_template(
        "project_detail.html",
        project=membership.project,
        membership=membership,
    )


@projects_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    """Chỉnh sửa dự án (PB06) - chỉ Trưởng nhóm."""
    membership = ProjectMember.query.filter_by(
        project_id=project_id, user_id=current_user.id
    ).first()

    if membership is None:
        flash("Bạn không có quyền truy cập dự án này.", "danger")
        return redirect(url_for("projects.list_projects"))

    if membership.role != "LEADER":
        flash("Chỉ trưởng nhóm được sửa dự án.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    project = membership.project

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        due_date_text = request.form.get("due_date", "").strip()

        if not name:
            flash("Tên dự án là bắt buộc.", "danger")
            return render_template("edit_project.html", project=project)

        if len(name) > 150:
            flash("Tên dự án không được dài quá 150 ký tự.", "danger")
            return render_template("edit_project.html", project=project)

        due_date = None
        if due_date_text:
            try:
                due_date = date.fromisoformat(due_date_text)
            except ValueError:
                flash("Hạn dự kiến không hợp lệ.", "danger")
                return render_template("edit_project.html", project=project)

        project.name = name
        project.description = description
        project.due_date = due_date

        # Nếu dự án từng bị Admin từ chối, sau khi sửa xong sẽ chuyển lại về PENDING để duyệt lại
        if project.approval_status == "REJECTED":
            project.approval_status = "PENDING"
            project.reject_reason = None
            flash("Dự án đã được cập nhật và gửi duyệt lại cho Quản trị viên.", "info")

        try:
            db.session.commit()
            flash("Cập nhật dự án thành công.", "success")
        except Exception:
            db.session.rollback()
            flash("Không thể cập nhật dự án.", "danger")
            return render_template("edit_project.html", project=project)

        return redirect(url_for("projects.project_detail", project_id=project.id))

    return render_template("edit_project.html", project=project)


@projects_bp.route("/<int:project_id>/members/add", methods=["POST"])
@login_required
def add_member(project_id):
    """Thêm thành viên vào dự án theo Email (PB08)."""
    project = Project.query.get_or_404(project_id)

    # Kiểm tra quyền Trưởng nhóm
    membership = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not membership or membership.role != "LEADER":
        flash("Chỉ trưởng nhóm mới có quyền thêm thành viên.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    # Kiểm tra quy tắc nghiệp vụ: Dự án phải ĐÃ DUYỆT mới cho thêm thành viên
    if project.approval_status != "APPROVED":
        flash("Dự án phải được Quản trị viên phê duyệt trước khi thêm thành viên.", "warning")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    email = request.form.get("email", "").strip().lower()
    if not email:
        flash("Vui lòng nhập email thành viên cần thêm.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    target_user = User.query.filter_by(email=email).first()
    if not target_user:
        flash(f"Không tìm thấy người dùng với email: {email}", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    # Kiểm tra xem đã là thành viên chưa
    existing_member = ProjectMember.query.filter_by(project_id=project_id, user_id=target_user.id).first()
    if existing_member:
        flash(f"Người dùng {target_user.full_name} ({email}) đã là thành viên của dự án.", "info")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    new_member = ProjectMember(
        project_id=project_id,
        user_id=target_user.id,
        role="MEMBER"
    )
    db.session.add(new_member)
    db.session.commit()

    flash(f"Đã thêm thành viên '{target_user.full_name}' vào dự án thành công!", "success")
    return redirect(url_for("projects.project_detail", project_id=project_id))


@projects_bp.route("/<int:project_id>/members/<int:user_id>/remove", methods=["POST"])
@login_required
def remove_member(project_id, user_id):
    """Xóa thành viên khỏi dự án (PB08)."""
    membership = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not membership or membership.role != "LEADER":
        flash("Chỉ trưởng nhóm mới có quyền loại bỏ thành viên.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    if user_id == current_user.id:
        flash("Trưởng nhóm không thể tự rời khỏi dự án.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    target_membership = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if target_membership:
        db.session.delete(target_membership)
        db.session.commit()
        flash("Đã loại bỏ thành viên khỏi dự án.", "info")

    return redirect(url_for("projects.project_detail", project_id=project_id))


@projects_bp.route("/<int:project_id>/discussions/create", methods=["POST"])
@login_required
def create_discussion(project_id):
    """Gửi thảo luận trong dự án (PB20)."""
    membership = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not membership and not current_user.is_admin:
        flash("Bạn không phải thành viên nên không thể gửi thảo luận.", "danger")
        return redirect(url_for("projects.list_projects"))

    content = request.form.get("content", "").strip()
    if not content:
        flash("Nội dung thảo luận không được để trống.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    new_msg = ProjectDiscussion(
        project_id=project_id,
        user_id=current_user.id,
        content=content
    )
    db.session.add(new_msg)
    db.session.commit()

    flash("Đã gửi tin nhắn thảo luận thành công!", "success")
    return redirect(url_for("projects.project_detail", project_id=project_id))
