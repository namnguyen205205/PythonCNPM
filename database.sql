-- =============================================================================
-- HE THONG QUAN LY DU AN NHOM CHO SINH VIEN (POSTGRESQL / SQL SCRIPT)
-- Mon hoc: Cong nghe Phan mem - Nhom 3
-- Phien ban: 1.1 (Co phan he Quan tri vien Admin)
-- =============================================================================

-- 1. XOA CAC BANG CU NEU DA TON TAI
DROP TABLE IF EXISTS project_discussions CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS project_members CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- =============================================================================
-- 2. TAO BANG DU LIEU
-- =============================================================================

-- Bang 1: Nguoi dung (Sinh vien & Quan tri vien)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT,
    system_role VARCHAR(20) NOT NULL DEFAULT 'USER', -- 'USER' hoac 'ADMIN'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,          -- TRUE = Hoat dong, FALSE = Bi khoa
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_users_email ON users (email);

-- Bang 2: Du an hoc tap
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    due_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',          -- 'ACTIVE' hoac 'ARCHIVED'
    approval_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',-- 'PENDING', 'APPROVED', 'REJECTED'
    created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP WITHOUT TIME ZONE,
    reject_reason TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bang 3: Thanh vien tham gia du an
CREATE TABLE project_members (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'MEMBER', -- 'LEADER' hoac 'MEMBER'
    joined_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_project_member UNIQUE (project_id, user_id)
);

-- Bang 4: Cong viec trong du an (Task)
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    assignee_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'TODO',     -- 'TODO', 'IN_PROGRESS', 'DONE'
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM', -- 'LOW', 'MEDIUM', 'HIGH'
    due_date DATE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bang 5: Thao luan noi bo nhom
CREATE TABLE project_discussions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 3. CHEN DU LIEU MAU DEMO (SEED DATA)
-- Tat ca tai khoan co mat khau mac dinh: 123456
-- (Chuoi hash pbkdf2 cua '123456')
-- =============================================================================

-- Chen tai khoan: 1 Admin va 3 Sinh vien
INSERT INTO users (id, full_name, email, password_hash, system_role, is_active, created_at) VALUES
(1, 'Quản trị viên', 'admin@gmail.com', 'scrypt:32768:8:1$n6fK7E6B8hN2$60538a7c2e5b7b9138e68406f52e5d9c72e276f7c8b0244db8f1d7a968eb1e27', 'ADMIN', TRUE, CURRENT_TIMESTAMP),
(2, 'Nguyễn Văn A', 'sinhvien_a@gmail.com', 'scrypt:32768:8:1$n6fK7E6B8hN2$60538a7c2e5b7b9138e68406f52e5d9c72e276f7c8b0244db8f1d7a968eb1e27', 'USER', TRUE, CURRENT_TIMESTAMP),
(3, 'Trần Thị B', 'sinhvien_b@gmail.com', 'scrypt:32768:8:1$n6fK7E6B8hN2$60538a7c2e5b7b9138e68406f52e5d9c72e276f7c8b0244db8f1d7a968eb1e27', 'USER', TRUE, CURRENT_TIMESTAMP),
(4, 'Lê Văn C', 'sinhvien_c@gmail.com', 'scrypt:32768:8:1$n6fK7E6B8hN2$60538a7c2e5b7b9138e68406f52e5d9c72e276f7c8b0244db8f1d7a968eb1e27', 'USER', TRUE, CURRENT_TIMESTAMP);

SELECT setval('users_id_seq', 4);

-- Chen Du an 1: Da duyet (APPROVED)
INSERT INTO projects (id, name, description, due_date, status, approval_status, created_by, reviewed_by, reviewed_at, created_at) VALUES
(1, 'Xây dựng Website Quản lý Nhóm CNPM', 'Đồ án học phần Công nghệ phần mềm - Nhóm 3 người', '2026-12-30', 'ACTIVE', 'APPROVED', 2, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Chen Du an 2: Cho duyet (PENDING) de demo chuc nang Admin duyet du an
INSERT INTO projects (id, name, description, due_date, status, approval_status, created_by, created_at) VALUES
(2, 'Nghiên cứu ứng dụng IoT trong nông nghiệp', 'Đồ án môn Hệ thống nhúng', '2026-11-20', 'ACTIVE', 'PENDING', 3, CURRENT_TIMESTAMP);

SELECT setval('projects_id_seq', 2);

-- Chen thanh vien vao Du an 1
INSERT INTO project_members (project_id, user_id, role, joined_at) VALUES
(1, 2, 'LEADER', CURRENT_TIMESTAMP),
(1, 3, 'MEMBER', CURRENT_TIMESTAMP),
(1, 4, 'MEMBER', CURRENT_TIMESTAMP),
(2, 3, 'LEADER', CURRENT_TIMESTAMP);

-- Chen cac Task vao Du an 1 (co 1 DONE, 1 IN_PROGRESS, 1 TODO de do % tien do)
INSERT INTO tasks (project_id, title, description, assignee_id, status, priority, due_date, created_at) VALUES
(1, 'Khảo sát yêu cầu và viết Product Backlog', 'Thu thập tài liệu và phân tích User Stories', 2, 'DONE', 'HIGH', '2026-11-15', CURRENT_TIMESTAMP),
(1, 'Thiết kế CSDL và viết models Flask', 'Xây dựng bảng PostgreSQL và migration', 3, 'IN_PROGRESS', 'HIGH', '2026-11-25', CURRENT_TIMESTAMP),
(1, 'Thiết kế giao diện Bootstrap và kiểm thử', 'Xây dựng template basic và viết unit test', 4, 'TODO', 'MEDIUM', '2026-12-10', CURRENT_TIMESTAMP);

-- Chen Thao luan vao Du an 1
INSERT INTO project_discussions (project_id, user_id, content, created_at) VALUES
(1, 2, 'Chào cả nhóm, mình đã chia các task chính trong đồ án rồi nhé!', CURRENT_TIMESTAMP),
(1, 3, 'Ok bạn, phần thiết kế CSDL mình đang làm dở, dự kiến mai xong.', CURRENT_TIMESTAMP);
