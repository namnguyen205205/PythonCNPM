from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Khởi tạo đối tượng ORM quản lý database
db = SQLAlchemy()

# Khởi tạo đối tượng quản lý phiên đăng nhập
login_manager = LoginManager()

# Cấu hình hành vi khi người dùng chưa đăng nhập mà truy cập trang bảo vệ
login_manager.login_view = "auth.login"
login_manager.login_message = "Bạn cần đăng nhập để xem trang này."
login_manager.login_message_category = "warning"

# Khởi tạo đối tượng quản lý migration CSDL (sau này dùng khi thay đổi bảng)
migrate = Migrate()