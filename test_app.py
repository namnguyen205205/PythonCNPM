import os
import unittest


# Phải thiết lập trước khi import app.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"

from app import (  # noqa: E402
    Project,
    ProjectMember,
    User,
    app,
    db,
)


class Sprint1TestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False

        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def register_user(
        self,
        full_name="Nguyễn Văn A",
        email="a@example.com",
        password="123456",
    ):
        return self.client.post(
            "/register",
            data={
                "full_name": full_name,
                "email": email,
                "password": password,
                "confirm_password": password,
            },
            follow_redirects=False,
        )

    def login_user(
        self,
        email="a@example.com",
        password="123456",
    ):
        return self.client.post(
            "/login",
            data={
                "email": email,
                "password": password,
            },
            follow_redirects=False,
        )

    def test_register_successfully(self):
        response = self.register_user()

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

        with app.app_context():
            user = User.query.filter_by(
                email="a@example.com",
            ).first()

            self.assertIsNotNone(user)
            self.assertNotEqual(
                user.password_hash,
                "123456",
            )

    def test_cannot_register_duplicate_email(self):
        self.register_user()
        response = self.register_user()

        self.assertEqual(response.status_code, 200)

        with app.app_context():
            number_of_users = User.query.filter_by(
                email="a@example.com",
            ).count()

            self.assertEqual(number_of_users, 1)

    def test_login_successfully(self):
        self.register_user()
        response = self.login_user()

        self.assertEqual(response.status_code, 302)

        with self.client.session_transaction() as session:
            self.assertIn("_user_id", session)

    def test_login_with_wrong_password(self):
        self.register_user()

        response = self.login_user(
            password="sai-mat-khau",
        )

        self.assertEqual(response.status_code, 200)

        with self.client.session_transaction() as session:
            self.assertNotIn("_user_id", session)

    def test_projects_require_login(self):
        response = self.client.get(
            "/projects",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_creator_becomes_project_leader(self):
        self.register_user()
        self.login_user()

        response = self.client.post(
            "/projects/create",
            data={
                "name": "Đồ án Công nghệ phần mềm",
                "description": "Hệ thống quản lý dự án",
                "due_date": "2026-12-31",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/projects", response.location)

        with app.app_context():
            project = Project.query.first()
            membership = ProjectMember.query.first()

            self.assertIsNotNone(project)
            self.assertIsNotNone(membership)
            self.assertEqual(
                membership.project_id,
                project.id,
            )
            self.assertEqual(
                membership.role,
                "LEADER",
            )

    def test_logout_removes_login_session(self):
        self.register_user()
        self.login_user()

        response = self.client.post(
            "/logout",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)

        with self.client.session_transaction() as session:
            self.assertNotIn("_user_id", session)


if __name__ == "__main__":
    unittest.main()
    