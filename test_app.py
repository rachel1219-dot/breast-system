# -*- coding: utf-8 -*-
"""
乳腺癌辅助诊断系统 - Vercel 部署诊断版本
"""
import os
import sys

print("[DIAGNOSTIC] Starting app initialization...")
print(f"[DIAGNOSTIC] Python version: {sys.version}")
print(f"[DIAGNOSTIC] Current working directory: {os.getcwd()}")
print(f"[DIAGNOSTIC] VERCEL env: {os.getenv('VERCEL', 'NOT SET')}")
print(f"[DIAGNOSTIC] FLASK_ENV: {os.getenv('FLASK_ENV', 'NOT SET')}")

try:
    from flask import Flask, render_template, jsonify
    print("[DIAGNOSTIC] Flask imported successfully")
except Exception as e:
    print(f"[DIAGNOSTIC] Flask import failed: {e}")
    sys.exit(1)

# 创建Flask应用
app = Flask(__name__)
print("[DIAGNOSTIC] Flask app created")

app.url_map.strict_slashes = False
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'test_secret_key')
print("[DIAGNOSTIC] App secret key set")

@app.route('/')
def home():
    print("[DIAGNOSTIC] / route accessed")
    return "Breast Cancer Detection System - Diagnostic Mode"

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "App is running"})

@app.route('/test')
def test():
    return jsonify({
        "status": "ok",
        "vercel": os.getenv('VERCEL', 'NOT SET'),
        "flask_env": os.getenv('FLASK_ENV', 'NOT SET'),
        "python_version": sys.version
    })

print("[DIAGNOSTIC] Routes registered")

# Vercel WSGI 入口
application = app
print("[DIAGNOSTIC] WSGI application exposed")

if __name__ == '__main__':
    print("[DIAGNOSTIC] Starting Flask development server")
    app.run(debug=True)
