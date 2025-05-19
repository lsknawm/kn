-- 创建数据库 KN
CREATE DATABASE IF NOT EXISTS KN;

-- 使用数据库 KN
USE KN;

-- 创建 users 表，用于存储用户登录信息
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建 user_info 表，用于存储用户个人信息
CREATE TABLE IF NOT EXISTS user_info (
    info_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(100),
    age INT,
    gender ENUM('Male', 'Female', 'Other'),
    profile_picture VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);