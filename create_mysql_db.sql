-- Script SQL para crear base de datos de Sistema de Asesoría Migratoria
-- Ejecutar en MySQL Workbench

-- 1. Crear base de datos
CREATE DATABASE IF NOT EXISTS immigration_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE immigration_dev;

-- 2. Crear tablas
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    permissions_json TEXT
) ENGINE=InnoDB;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB;

CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_number VARCHAR(50) UNIQUE NOT NULL,
    primary_name VARCHAR(200) NOT NULL,
    case_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'intake',
    priority VARCHAR(20) DEFAULT 'normal',
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deadline_date DATETIME NULL,
    assigned_to INT NULL,
    created_by INT NOT NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_case_number (case_number)
) ENGINE=InnoDB;

CREATE TABLE family_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    role VARCHAR(50) NOT NULL,
    relationship VARCHAR(50),
    dob DATE NULL,
    email VARCHAR(120),
    phone VARCHAR(20),
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE forms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    form_number VARCHAR(50) NOT NULL,
    form_title VARCHAR(200),
    status VARCHAR(50) DEFAULT 'not_started',
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    interview_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    transcript TEXT,
    summary TEXT,
    conducted_by INT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (conducted_by) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE case_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    content TEXT NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB;

-- 3. Insertar rol admin
INSERT INTO roles (name, description, permissions_json) VALUES 
('admin', 'Administrador', '{"manage_users":true,"manage_clients":true,"view_all_cases":true,"edit_all_cases":true,"delete_cases":true}');

-- 4. Insertar usuario admin (password: admin123)
INSERT INTO users (username, email, password_hash, first_name, last_name, role_id) VALUES 
('admin', 'admin@test.com', 'scrypt:32768:8:1$abc$def123', 'Admin', 'User', 1);

SELECT '✅ Base de datos creada' as status;
