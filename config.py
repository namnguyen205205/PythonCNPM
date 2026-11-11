import os
from dotenv import load_dotenv

# Đọc file .env và nạp các biến (SECRET_KEY, DATABASE_URL) vào môi trường
load_dotenv()


class Config:
    """Cấu hình dùng khi chạy ứng dụng bình thường."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Lấy từ .env; nếu .env không có thì dùng SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///project_manager.db",
    )

    # Tắt tính năng theo dõi thay đổi của SQLAlchemy (tốn bộ nhớ, không cần dùng)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """Cấu hình dùng khi chạy pytest."""

    TESTING = True
    # Database nằm trong RAM: mỗi lần test là một database mới, sạch
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Tắt kiểm tra CSRF khi test (khi nào thêm form có CSRF mới cần đến)
    WTF_CSRF_ENABLED = False