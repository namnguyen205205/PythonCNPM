import click
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import User

app = create_app()


@app.cli.command("create-admin")
@click.argument("email")
@click.argument("full_name")
@click.argument("password")
def create_admin(email, full_name, password):
    """Lệnh CLI tạo tài khoản Quản trị viên (Admin) đầu tiên."""
    with app.app_context():
        user = User.query.filter_by(email=email.strip().lower()).first()
        if user:
            click.echo(f"Lỗi: Email {email} đã tồn tại trong hệ thống!")
            return

        admin_user = User(
            email=email.strip().lower(),
            full_name=full_name.strip(),
            password_hash=generate_password_hash(password),
            system_role="ADMIN",
            is_active=True,
        )
        db.session.add(admin_user)
        db.session.commit()
        click.echo(f"Thành công: Đã tạo Quản trị viên '{full_name}' ({email})!")


if __name__ == "__main__":
    app.run(debug=True)