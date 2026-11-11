from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    """Decorator kiểm tra quyền Quản trị viên (Admin)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Nếu chưa đăng nhập hoặc không phải Admin -> Chặn truy cập 403
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function