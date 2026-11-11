from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate
from app.routers.tasks import tasks_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Đăng ký các Blueprint
    from app.routers.auth import auth_bp
    from app.routers.projects import projects_bp
    from app.routers.admin import admin_bp
    from app.routers.tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(admin_bp)
    app.register_blueprint(tasks_bp)

    @app.route("/")
    def index():
        from flask import redirect, url_for
        return redirect(url_for("projects.list_projects"))

    return app