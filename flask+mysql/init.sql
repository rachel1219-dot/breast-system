-- ============================================
-- Flask + MySQL 学生管理系统 - 数据库初始化
-- ============================================

-- 1. 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS student_db
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE student_db;

-- 2. 查看数据库是否创建成功
SHOW DATABASES;

-- 3. 查看当前数据库中的表（运行Flask应用后会自动创建）
SHOW TABLES;

-- 4. 查看students表结构（ORM会自动创建）
DESC students;

-- ============================================
-- MySQL 连接参数说明
-- ============================================
-- 格式: mysql+pymysql://用户名:密码@服务器:端口/数据库名
--
-- 示例: mysql+pymysql://root:123456@localhost:3306/student_db
--       mysql+pymysql://root:你的密码@localhost:3306/student_db
--
-- 如果使用远程MySQL服务器，将 localhost 替换为服务器IP
