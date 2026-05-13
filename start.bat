@echo off
chcp 65001 >nul
title 乳腺癌智能诊断系统 - 启动脚本
echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║       乳腺癌智能诊断系统 - 一键启动                  ║
echo ║  Flask + MySQL 8.0 + RandomForest + DeepSeek API    ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 安装依赖
echo [1/3] 安装 Python 依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [WARN] 部分依赖安装可能失败，如果 mysqlclient 失败请参考 README
)

:: 提示配置
echo.
echo [2/3] 配置检查...
echo 请确认以下配置（编辑 .env 文件）:
echo   - MYSQL_HOST / MYSQL_PORT / MYSQL_USER / MYSQL_PASSWORD
echo   - DEEPSEEK_API_KEY（可选，不配置则使用提示模式）
echo.

:: 启动
echo [3/3] 启动 Flask 服务器...
echo.
echo ✅ 访问地址: http://localhost:5000
echo ✅ 首次访问首页，点击"进入系统"跳转登录/注册页面
echo ✅ 按 Ctrl+C 停止服务器
echo.
python app.py

pause
