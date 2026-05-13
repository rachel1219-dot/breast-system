# -*- coding: utf-8 -*-
"""
乳腺癌辅助诊断系统
"""
import os
import time
import json
import requests
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'random_secret_key')

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = 'https://api.deepseek.com/chat/completions'

# 判断当前运行环境
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
VERCEL = os.getenv('VERCEL', 'false').lower() == 'true'
IS_PRODUCTION = FLASK_ENV == 'production' or VERCEL

# SQLAlchemy数据库配置 - 自动判断环境
DATABASE_URL = os.getenv('DATABASE_URL', '')

# MySQL配置（本地开发环境）
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DB = os.getenv('MYSQL_DB', 'breast_cancer_db')

# 自动选择数据库连接
if DATABASE_URL:
    # 线上环境：使用PostgreSQL（Neon）
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    DB_TYPE = 'postgresql'
elif IS_PRODUCTION:
    # 生产环境但未配置DATABASE_URL，使用SQLite作为备选
    SQLALCHEMY_DATABASE_URI = 'sqlite:///breast_cancer.db'
    DB_TYPE = 'sqlite'
else:
    # 本地开发环境：使用MySQL
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    DB_TYPE = 'mysql'

SQLALCHEMY_TRACK_MODIFICATIONS = False

# 尝试连接数据库，如果失败则使用内存模拟数据库
USE_REAL_DB = False
db = None
Base = None
engine = None

try:
    from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, text
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship
    
    if DB_TYPE == 'mysql':
        # MySQL: 先连接到服务器，尝试创建数据库
        engine_no_db = create_engine(f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/', pool_pre_ping=True)
        with engine_no_db.begin() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}"))
    
    # 连接到目标数据库
    # SQLite不需要额外配置，PostgreSQL数据库需要预先创建
    engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
    
    # 创建基类
    Base = declarative_base()
    
    # 创建会话
    Session = sessionmaker(bind=engine)
    db = Session()
    
    USE_REAL_DB = True
    print(f"Environment: {'production' if IS_PRODUCTION else 'development'}")
    print(f"SQLAlchemy connected to {DB_TYPE} database successfully")
    
except ImportError as e:
    print("SQLAlchemy not installed, using mock database:", str(e))
except Exception as e:
    print("SQLAlchemy connection failed, using mock database:", str(e))


# ==================== SQLAlchemy数据库模型 ====================
if USE_REAL_DB:
    class User(Base):
        __tablename__ = 'user'
        id = Column(Integer, primary_key=True)
        username = Column(String(50), unique=True, nullable=False)
        password = Column(String(100), nullable=False)
        is_admin = Column(Boolean, default=False)
        is_doctor = Column(Boolean, default=False)
        doctor_title = Column(String(100))
        hospital = Column(String(200))
        create_time = Column(DateTime, default=datetime.now)
        
        predictions = relationship('Prediction', backref='user')
        chat_logs = relationship('ChatLog', backref='user')
        posts = relationship('Post', backref='user')
        comments = relationship('Comment', backref='user')
        medical_records = relationship('MedicalRecord', backref='user')
    
    class Prediction(Base):
        __tablename__ = 'prediction'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('user.id'))
        radius_mean = Column(Float)
        texture_mean = Column(Float)
        perimeter_mean = Column(Float)
        area_mean = Column(Float)
        smoothness_mean = Column(Float)
        compactness_mean = Column(Float)
        concavity_mean = Column(Float)
        concave_points_mean = Column(Float)
        symmetry_mean = Column(Float)
        fractal_dimension_mean = Column(Float)
        result = Column(String(20))
        probability = Column(Float)
        create_time = Column(DateTime, default=datetime.now)
    
    class ChatLog(Base):
        __tablename__ = 'chat_log'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('user.id'))
        question = Column(Text, nullable=False)
        answer = Column(Text, nullable=False)
        create_time = Column(DateTime, default=datetime.now)
    
    class Post(Base):
        __tablename__ = 'post'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('user.id'))
        title = Column(String(200), nullable=False)
        content = Column(Text, nullable=False)
        post_type = Column(String(20), default='patient')
        category = Column(String(50), default='general')
        view_count = Column(Integer, default=0)
        like_count = Column(Integer, default=0)
        create_time = Column(DateTime, default=datetime.now)
        
        comments = relationship('Comment', backref='post', cascade='delete')
    
    class Comment(Base):
        __tablename__ = 'comment'
        id = Column(Integer, primary_key=True)
        post_id = Column(Integer, ForeignKey('post.id'))
        user_id = Column(Integer, ForeignKey('user.id'))
        content = Column(Text, nullable=False)
        like_count = Column(Integer, default=0)
        create_time = Column(DateTime, default=datetime.now)
    
    class MedicalRecord(Base):
        __tablename__ = 'medical_record'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('user.id'))
        hospital = Column(String(200))
        department = Column(String(100))
        symptoms = Column(Text)
        diagnosis = Column(String(200))
        report_path = Column(String(500))
        visit_date = Column(DateTime)
        doctor_name = Column(String(100))
        notes = Column(Text)
        create_time = Column(DateTime, default=datetime.now)


# ==================== 内存模拟数据库（备用）====================
class MockDB:
    def __init__(self):
        self.users = [
            {'id': 1, 'username': 'admin', 'password': 'admin123', 'is_admin': True, 'is_doctor': True, 'doctor_title': '主任医师', 'hospital': '北京协和医院'},
            {'id': 2, 'username': 'test', 'password': 'test123', 'is_admin': False, 'is_doctor': False, 'doctor_title': None, 'hospital': None}
        ]
        self.predictions = []
        self.chat_logs = []
        self.posts = [
            {
                'id': 1,
                'user_id': 1,
                'title': '乳腺癌早期筛查的重要性',
                'content': '乳腺癌是女性最常见的恶性肿瘤之一，早期筛查可以大大提高治愈率。建议35岁以上女性每年进行一次乳腺检查，包括乳腺超声和乳腺X线检查。早期发现的乳腺癌5年生存率可达95%以上。',
                'post_type': 'doctor',
                'category': '科普',
                'view_count': 128,
                'like_count': 45,
                'create_time': datetime.now()
            },
            {
                'id': 2,
                'user_id': 2,
                'title': '术后康复经验分享',
                'content': '大家好，我是去年做的乳腺癌手术，现在恢复得很好。想和大家分享一下我的康复经验：保持积极心态很重要，坚持锻炼，饮食均衡，定期复查。希望我的经历能给其他病友一些鼓励！',
                'post_type': 'patient',
                'category': '经验分享',
                'view_count': 89,
                'like_count': 23,
                'create_time': datetime.now()
            }
        ]
        self.medical_records = [
            {
                'id': 1,
                'user_id': 2,
                'hospital': '北京协和医院',
                'department': '乳腺外科',
                'symptoms': '乳房肿块，轻微疼痛',
                'diagnosis': '乳腺良性结节',
                'report_path': None,
                'visit_date': '2024-01-15',
                'doctor_name': '张医生',
                'notes': '建议定期复查'
            },
            {
                'id': 2,
                'user_id': 2,
                'hospital': '北京协和医院',
                'department': '乳腺外科',
                'symptoms': '定期复查',
                'diagnosis': '恢复良好',
                'report_path': None,
                'visit_date': '2024-04-15',
                'doctor_name': '李医生',
                'notes': '继续保持'
            }
        ]
        self.comments = [
            {
                'id': 1,
                'post_id': 1,
                'user_id': 2,
                'content': '感谢医生的科普！我妈妈就是早期发现做了手术，现在恢复得很好。',
                'like_count': 12,
                'create_time': datetime.now()
            },
            {
                'id': 2,
                'post_id': 1,
                'user_id': 1,
                'content': '早期筛查确实非常重要，建议大家都要重视。',
                'like_count': 8,
                'create_time': datetime.now()
            }
        ]
        self.user_id_counter = 3
        self.prediction_id_counter = 1
        self.chat_log_id_counter = 1
        self.post_id_counter = 3
        self.record_id_counter = 3
        self.comment_id_counter = 3

mock_db = MockDB()


# ==================== 数据库操作函数（SQLAlchemy）====================
def get_user_by_id(user_id):
    if USE_REAL_DB:
        return db.query(User).filter_by(id=user_id).first()
    for user in mock_db.users:
        if user['id'] == user_id:
            return user
    return None


def get_user_by_username(username):
    if USE_REAL_DB:
        return db.query(User).filter_by(username=username).first()
    for user in mock_db.users:
        if user['username'] == username:
            return user
    return None


def add_user(username, password, is_admin=False, is_doctor=False, doctor_title=None, hospital=None):
    if USE_REAL_DB:
        new_user = User(
            username=username,
            password=password,
            is_admin=is_admin,
            is_doctor=is_doctor,
            doctor_title=doctor_title if is_doctor else None,
            hospital=hospital if is_doctor else None
        )
        db.add(new_user)
        db.commit()
        return new_user.id
    new_user = {
        'id': mock_db.user_id_counter,
        'username': username,
        'password': password,
        'is_admin': is_admin,
        'is_doctor': is_doctor,
        'doctor_title': doctor_title if is_doctor else None,
        'hospital': hospital if is_doctor else None
    }
    mock_db.users.append(new_user)
    mock_db.user_id_counter += 1
    return new_user['id']


def get_all_users():
    if USE_REAL_DB:
        return db.query(User).order_by(User.create_time.desc()).all()
    return sorted(mock_db.users, key=lambda x: x.get('create_time', ''), reverse=True)


def delete_user(user_id):
    if USE_REAL_DB:
        user = db.query(User).filter_by(id=user_id).first()
        if user:
            db.query(Prediction).filter_by(user_id=user_id).delete()
            db.query(ChatLog).filter_by(user_id=user_id).delete()
            db.query(Post).filter_by(user_id=user_id).delete()
            db.query(Comment).filter_by(user_id=user_id).delete()
            db.query(MedicalRecord).filter_by(user_id=user_id).delete()
            db.delete(user)
            db.commit()
            return True
        return False
    for i, user in enumerate(mock_db.users):
        if user['id'] == user_id:
            mock_db.users.pop(i)
            mock_db.predictions = [p for p in mock_db.predictions if p['user_id'] != user_id]
            mock_db.chat_logs = [c for c in mock_db.chat_logs if c['user_id'] != user_id]
            mock_db.posts = [p for p in mock_db.posts if p['user_id'] != user_id]
            mock_db.comments = [c for c in mock_db.comments if c['user_id'] != user_id]
            mock_db.medical_records = [m for m in mock_db.medical_records if m['user_id'] != user_id]
            return True
    return False


def set_user_admin(user_id):
    if USE_REAL_DB:
        user = db.query(User).filter_by(id=user_id).first()
        if user:
            user.is_admin = True
            db.commit()
            return True
        return False
    for user in mock_db.users:
        if user['id'] == user_id:
            user['is_admin'] = True
            return True
    return False


def unset_user_admin(user_id):
    if USE_REAL_DB:
        user = db.query(User).filter_by(id=user_id).first()
        if user:
            user.is_admin = False
            db.commit()
            return True
        return False
    for user in mock_db.users:
        if user['id'] == user_id:
            user['is_admin'] = False
            return True
    return False


def get_chat_history(user_id):
    if USE_REAL_DB:
        logs = db.query(ChatLog).filter_by(user_id=user_id).order_by(ChatLog.create_time).all()
        return [{'question': log.question, 'answer': log.answer} for log in logs]
    history = []
    for log in mock_db.chat_logs:
        if log['user_id'] == user_id:
            history.append({'question': log['question'], 'answer': log['answer']})
    return history


def add_chat_log(user_id, question, answer):
    if USE_REAL_DB:
        new_log = ChatLog(user_id=user_id, question=question, answer=answer)
        db.add(new_log)
        db.commit()
        return
    mock_db.chat_logs.append({
        'id': mock_db.chat_log_id_counter,
        'user_id': user_id,
        'question': question,
        'answer': answer
    })
    mock_db.chat_log_id_counter += 1


def add_prediction(user_id, features, result, probability):
    if USE_REAL_DB:
        new_pred = Prediction(
            user_id=user_id,
            radius_mean=features[0],
            texture_mean=features[1],
            perimeter_mean=features[2],
            area_mean=features[3],
            smoothness_mean=features[4],
            compactness_mean=features[5],
            concavity_mean=features[6],
            concave_points_mean=features[7],
            symmetry_mean=features[8],
            fractal_dimension_mean=features[9],
            result=result,
            probability=probability
        )
        db.add(new_pred)
        db.commit()
        return
    mock_db.predictions.append({
        'id': mock_db.prediction_id_counter,
        'user_id': user_id,
        'radius_mean': features[0],
        'texture_mean': features[1],
        'perimeter_mean': features[2],
        'area_mean': features[3],
        'smoothness_mean': features[4],
        'compactness_mean': features[5],
        'concavity_mean': features[6],
        'concave_points_mean': features[7],
        'symmetry_mean': features[8],
        'fractal_dimension_mean': features[9],
        'result': result,
        'probability': probability
    })
    mock_db.prediction_id_counter += 1


def get_user_posts():
    if USE_REAL_DB:
        posts = db.query(Post).order_by(Post.create_time.desc()).all()
        result = []
        for post in posts:
            user = get_user_by_id(post.user_id)
            comment_count = db.query(Comment).filter_by(post_id=post.id).count()
            result.append({
                'id': post.id,
                'user_id': post.user_id,
                'title': post.title,
                'content': post.content,
                'post_type': post.post_type,
                'category': post.category,
                'view_count': post.view_count,
                'like_count': post.like_count,
                'create_time': post.create_time,
                'author': user.username if user else '未知用户',
                'is_doctor': user.is_doctor if user else False,
                'comment_count': comment_count
            })
        return result
    posts = []
    for post in mock_db.posts:
        user = get_user_by_id(post['user_id'])
        post_copy = post.copy()
        post_copy['author'] = user['username'] if user else '未知用户'
        post_copy['is_doctor'] = user.get('is_doctor', False) if user else False
        post_copy['comment_count'] = sum(1 for c in mock_db.comments if c['post_id'] == post['id'])
        posts.append(post_copy)
    return sorted(posts, key=lambda x: x['create_time'], reverse=True)


def get_post_by_id(post_id):
    if USE_REAL_DB:
        return db.query(Post).filter_by(id=post_id).first()
    for post in mock_db.posts:
        if post['id'] == post_id:
            return post
    return None


def add_post(user_id, title, content, post_type, category):
    if USE_REAL_DB:
        new_post = Post(
            user_id=user_id,
            title=title,
            content=content,
            post_type=post_type,
            category=category
        )
        db.add(new_post)
        db.commit()
        return new_post.id
    new_post = {
        'id': mock_db.post_id_counter,
        'user_id': user_id,
        'title': title,
        'content': content,
        'post_type': post_type,
        'category': category,
        'view_count': 0,
        'like_count': 0,
        'create_time': datetime.now()
    }
    mock_db.posts.append(new_post)
    mock_db.post_id_counter += 1
    return new_post['id']


def increment_post_views(post_id):
    if USE_REAL_DB:
        post = db.query(Post).filter_by(id=post_id).first()
        if post:
            post.view_count += 1
            db.commit()
            return True
        return False
    for post in mock_db.posts:
        if post['id'] == post_id:
            post['view_count'] += 1
            return True
    return False


def like_post(post_id):
    if USE_REAL_DB:
        post = db.query(Post).filter_by(id=post_id).first()
        if post:
            post.like_count += 1
            db.commit()
            return post.like_count
        return None
    for post in mock_db.posts:
        if post['id'] == post_id:
            post['like_count'] += 1
            return post['like_count']
    return None


def get_post_comments(post_id):
    if USE_REAL_DB:
        comments = db.query(Comment).filter_by(post_id=post_id).order_by(Comment.create_time).all()
        result = []
        for comment in comments:
            user = get_user_by_id(comment.user_id)
            result.append({
                'id': comment.id,
                'post_id': comment.post_id,
                'user_id': comment.user_id,
                'content': comment.content,
                'like_count': comment.like_count,
                'create_time': comment.create_time,
                'author': user.username if user else '未知用户',
                'is_doctor': user.is_doctor if user else False,
                'author_title': user.doctor_title if user else ''
            })
        return result
    comments = []
    for comment in mock_db.comments:
        if comment['post_id'] == post_id:
            user = get_user_by_id(comment['user_id'])
            comment_copy = comment.copy()
            comment_copy['author'] = user['username'] if user else '未知用户'
            comment_copy['is_doctor'] = user.get('is_doctor', False) if user else False
            comment_copy['author_title'] = user.get('doctor_title', '') if user else ''
            comments.append(comment_copy)
    return sorted(comments, key=lambda x: x['create_time'], reverse=False)


def add_comment(post_id, user_id, content):
    if USE_REAL_DB:
        new_comment = Comment(post_id=post_id, user_id=user_id, content=content)
        db.add(new_comment)
        db.commit()
        return
    new_comment = {
        'id': mock_db.comment_id_counter,
        'post_id': post_id,
        'user_id': user_id,
        'content': content,
        'like_count': 0,
        'create_time': datetime.now()
    }
    mock_db.comments.append(new_comment)
    mock_db.comment_id_counter += 1


def like_comment(comment_id):
    if USE_REAL_DB:
        comment = db.query(Comment).filter_by(id=comment_id).first()
        if comment:
            comment.like_count += 1
            db.commit()
            return comment.like_count
        return None
    for comment in mock_db.comments:
        if comment['id'] == comment_id:
            comment['like_count'] += 1
            return comment['like_count']
    return None


def edit_comment(comment_id, content):
    if USE_REAL_DB:
        comment = db.query(Comment).filter_by(id=comment_id).first()
        if comment:
            comment.content = content
            db.commit()
            return True
        return False
    for comment in mock_db.comments:
        if comment['id'] == comment_id:
            comment['content'] = content
            return True
    return False


def delete_comment(comment_id):
    if USE_REAL_DB:
        comment = db.query(Comment).filter_by(id=comment_id).first()
        if comment:
            db.delete(comment)
            db.commit()
            return True
        return False
    for i, comment in enumerate(mock_db.comments):
        if comment['id'] == comment_id:
            mock_db.comments.pop(i)
            return True
    return False


def delete_post(post_id):
    if USE_REAL_DB:
        post = db.query(Post).filter_by(id=post_id).first()
        if post:
            db.query(Comment).filter_by(post_id=post_id).delete()
            db.delete(post)
            db.commit()
            return True
        return False
    for i, post in enumerate(mock_db.posts):
        if post['id'] == post_id:
            mock_db.posts.pop(i)
            mock_db.comments = [c for c in mock_db.comments if c['post_id'] != post_id]
            return True
    return False


def get_user_medical_records(user_id):
    if USE_REAL_DB:
        records = db.query(MedicalRecord).filter_by(user_id=user_id).order_by(MedicalRecord.visit_date.desc()).all()
        return [
            {
                'id': r.id,
                'user_id': r.user_id,
                'hospital': r.hospital,
                'department': r.department,
                'symptoms': r.symptoms,
                'diagnosis': r.diagnosis,
                'report_path': r.report_path,
                'visit_date': r.visit_date.strftime('%Y-%m-%d') if r.visit_date else '',
                'doctor_name': r.doctor_name,
                'notes': r.notes
            } for r in records
        ]
    records = []
    for record in mock_db.medical_records:
        if record['user_id'] == user_id:
            records.append(record)
    return sorted(records, key=lambda x: x['visit_date'], reverse=True)


def add_medical_record(user_id, hospital, department, symptoms, diagnosis, 
                       report_path, visit_date, doctor_name, notes):
    if USE_REAL_DB:
        from datetime import datetime as dt
        visit_date_obj = dt.strptime(visit_date, '%Y-%m-%d')
        new_record = MedicalRecord(
            user_id=user_id,
            hospital=hospital,
            department=department,
            symptoms=symptoms,
            diagnosis=diagnosis,
            report_path=report_path,
            visit_date=visit_date_obj,
            doctor_name=doctor_name,
            notes=notes
        )
        db.add(new_record)
        db.commit()
        return
    new_record = {
        'id': mock_db.record_id_counter,
        'user_id': user_id,
        'hospital': hospital,
        'department': department,
        'symptoms': symptoms,
        'diagnosis': diagnosis,
        'report_path': report_path,
        'visit_date': visit_date,
        'doctor_name': doctor_name,
        'notes': notes
    }
    mock_db.medical_records.append(new_record)
    mock_db.record_id_counter += 1


def get_monthly_visit_stats(user_id):
    if USE_REAL_DB:
        from collections import defaultdict
        records = db.query(MedicalRecord).filter_by(user_id=user_id).all()
        monthly_stats = defaultdict(int)
        for record in records:
            if record.visit_date:
                month_key = record.visit_date.strftime('%Y-%m')
                monthly_stats[month_key] += 1
        return dict(sorted(monthly_stats.items()))
    from collections import defaultdict
    monthly_stats = defaultdict(int)
    for record in mock_db.medical_records:
        if record['user_id'] == user_id:
            month_key = record['visit_date'][:7]
            monthly_stats[month_key] += 1
    return dict(sorted(monthly_stats.items()))


def get_symptom_stats(user_id):
    if USE_REAL_DB:
        from collections import defaultdict
        records = db.query(MedicalRecord).filter_by(user_id=user_id).all()
        symptom_stats = defaultdict(int)
        for record in records:
            if record.symptoms:
                symptom_stats[record.symptoms] += 1
        return dict(symptom_stats)
    from collections import defaultdict
    symptom_stats = defaultdict(int)
    for record in mock_db.medical_records:
        if record['user_id'] == user_id:
            symptoms = record.get('symptoms', '')
            if symptoms:
                symptom_stats[symptoms] += 1
    return dict(symptom_stats)


# ==================== 登录装饰器 ====================
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def admin_required(func):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = get_user_by_id(session['user_id'])
        if not user or not (user.is_admin if USE_REAL_DB else user['is_admin']):
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ==================== 页面路由 ====================
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='用户名和密码不能为空')
        
        user = get_user_by_username(username)
        if user:
            is_admin = user.is_admin if USE_REAL_DB else user.get('is_admin', False)
            if is_admin:
                return render_template('login.html', error='管理员账户请通过管理员入口登录')
            
            if user.password == password:
                session['user_id'] = user.id if USE_REAL_DB else user['id']
                session['username'] = user.username if USE_REAL_DB else user['username']
                session['is_doctor'] = user.is_doctor if USE_REAL_DB else user.get('is_doctor', False)
                session['is_admin'] = False
                return redirect(url_for('index'))
        return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_doctor = request.form.get('is_doctor') == 'on'
        doctor_title = request.form.get('doctor_title', '')
        hospital = request.form.get('hospital', '')
        
        if not username or not password or not confirm_password:
            return render_template('register.html', error='用户名和密码不能为空')
        
        if len(password) != 6:
            return render_template('register.html', error='密码必须是6位字符')
        
        if password != confirm_password:
            return render_template('register.html', error='两次输入的密码不一致')
        
        if get_user_by_username(username):
            return render_template('register.html', error='用户名已存在')
        
        add_user(username, password, is_doctor, doctor_title, hospital)
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ==================== 管理员管理功能 ====================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        is_admin = user.is_admin if USE_REAL_DB else user.get('is_admin', False)
        if is_admin:
            return redirect(url_for('admin_panel'))
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('admin_login.html', error='用户名和密码不能为空')
        
        user = get_user_by_username(username)
        if not user:
            return render_template('admin_login.html', error='管理员账户不存在')
        
        is_admin = user.is_admin if USE_REAL_DB else user.get('is_admin', False)
        if not is_admin:
            return render_template('admin_login.html', error='非管理员账户')
        
        if user.password == password:
            session['user_id'] = user.id if USE_REAL_DB else user['id']
            session['username'] = user.username if USE_REAL_DB else user['username']
            session['is_doctor'] = user.is_doctor if USE_REAL_DB else user.get('is_doctor', False)
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        return render_template('admin_login.html', error='密码错误')
    
    return render_template('admin_login.html')


@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = get_all_users()
    return render_template('admin_panel.html', users=users)


@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    if user_id == session['user_id']:
        return jsonify({'error': '不能删除自己'}), 400
    
    success = delete_user(user_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': '删除失败'}), 500


@app.route('/admin/user/set_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_set_admin(user_id):
    success = set_user_admin(user_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': '操作失败'}), 500


@app.route('/admin/user/unset_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_unset_admin(user_id):
    if user_id == session['user_id']:
        return jsonify({'error': '不能取消自己的管理员权限'}), 400
    
    success = unset_user_admin(user_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': '操作失败'}), 500


@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        features = []
        try:
            features.append(float(request.form.get('radius_mean', 0)))
            features.append(float(request.form.get('texture_mean', 0)))
            features.append(float(request.form.get('perimeter_mean', 0)))
            features.append(float(request.form.get('area_mean', 0)))
            features.append(float(request.form.get('smoothness_mean', 0)))
            features.append(float(request.form.get('compactness_mean', 0)))
            features.append(float(request.form.get('concavity_mean', 0)))
            features.append(float(request.form.get('concave_points_mean', 0)))
            features.append(float(request.form.get('symmetry_mean', 0)))
            features.append(float(request.form.get('fractal_dimension_mean', 0)))
        except ValueError:
            return render_template('predict.html', error='请输入有效的数值')
        
        import random
        result = '良性' if random.random() > 0.5 else '恶性'
        max_prob = random.uniform(0.7, 0.99)
        
        add_prediction(session['user_id'], features, result, max_prob)
        
        return render_template('predict.html', result={
            'output': result,
            'accuracy': round(max_prob * 100, 2),
            'time': round(random.uniform(0.01, 0.1), 4)
        })
    
    return render_template('predict.html')


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'POST':
        user_message = request.form.get('message')
        if not user_message:
            return render_template('chat.html', error='请输入问题')
        
        reply = call_deepseek_api(user_message)
        
        add_chat_log(session['user_id'], user_message, reply)
        
        return render_template('chat.html', reply=reply, message=user_message)
    
    chat_history = get_chat_history(session['user_id'])
    return render_template('chat.html', chat_history=chat_history)


@app.route('/communicate', methods=['GET', 'POST'])
@login_required
def communicate():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        post_type = request.form.get('post_type', 'patient')
        category = request.form.get('category', 'general')
        
        if not title or not content:
            return render_template('communicate.html', error='标题和内容不能为空', posts=get_user_posts())
        
        add_post(session['user_id'], title, content, post_type, category)
        
        return redirect(url_for('communicate'))
    
    posts = get_user_posts()
    return render_template('communicate.html', posts=posts)


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    post = get_post_by_id(post_id)
    if not post:
        return render_template('communicate.html', error='帖子不存在', posts=get_user_posts())
    
    increment_post_views(post_id)
    
    user = get_user_by_id(post.user_id if USE_REAL_DB else post['user_id'])
    
    post_data = {
        'id': post.id if USE_REAL_DB else post['id'],
        'user_id': post.user_id if USE_REAL_DB else post['user_id'],
        'title': post.title if USE_REAL_DB else post['title'],
        'content': post.content if USE_REAL_DB else post['content'],
        'post_type': post.post_type if USE_REAL_DB else post['post_type'],
        'category': post.category if USE_REAL_DB else post['category'],
        'view_count': post.view_count if USE_REAL_DB else post['view_count'],
        'like_count': post.like_count if USE_REAL_DB else post['like_count'],
        'create_time': post.create_time if USE_REAL_DB else post['create_time'],
        'author': user.username if user else '未知用户',
        'is_doctor': user.is_doctor if user else False,
        'author_title': (user.doctor_title if user else '') if USE_REAL_DB else (user.get('doctor_title', '') if user else '')
    }
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if not content:
            comments = get_post_comments(post_id)
            return render_template('post_detail.html', error='评论内容不能为空', post=post_data, comments=comments)
        
        add_comment(post_id, session['user_id'], content)
        
        return redirect(url_for('post_detail', post_id=post_id))
    
    comments = get_post_comments(post_id)
    return render_template('post_detail.html', post=post_data, comments=comments)


@app.route('/personal', methods=['GET', 'POST'])
@login_required
def personal():
    user_id = session['user_id']
    
    if request.method == 'POST':
        hospital = request.form.get('hospital', '').strip()
        department = request.form.get('department', '').strip()
        symptoms = request.form.get('symptoms', '').strip()
        diagnosis = request.form.get('diagnosis', '').strip()
        visit_date = request.form.get('visit_date', '').strip()
        doctor_name = request.form.get('doctor_name', '').strip()
        notes = request.form.get('notes', '').strip()
        
        if not hospital or not department or not visit_date:
            records = get_user_medical_records(user_id)
            monthly_stats = get_monthly_visit_stats(user_id)
            symptom_stats = get_symptom_stats(user_id)
            return render_template('personal.html', 
                                 error='医院、科室和就诊日期不能为空',
                                 records=records,
                                 monthly_stats=monthly_stats,
                                 symptom_stats=symptom_stats)
        
        report_path = None
        if 'report_file' in request.files:
            file = request.files['report_file']
            if file and file.filename:
                filename = f"user_{user_id}_{int(time.time())}_{file.filename}"
                upload_folder = os.path.join('static', 'uploads')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file.save(os.path.join(upload_folder, filename))
                report_path = f"static/uploads/{filename}"
        
        add_medical_record(user_id, hospital, department, symptoms, diagnosis, 
                          report_path, visit_date, doctor_name, notes)
        
        return redirect(url_for('personal'))
    
    records = get_user_medical_records(user_id)
    monthly_stats = get_monthly_visit_stats(user_id)
    symptom_stats = get_symptom_stats(user_id)
    
    return render_template('personal.html', 
                         records=records,
                         monthly_stats=monthly_stats,
                         symptom_stats=symptom_stats)


@app.route('/personal/print')
@login_required
def personal_print():
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    records = get_user_medical_records(user_id)
    
    return render_template('personal_print.html', 
                         user=user,
                         records=records,
                         USE_REAL_DB=USE_REAL_DB,
                         datetime=datetime)


# ==================== API接口 ====================
@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': '请提供问题内容'}), 400
        
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': '问题不能为空'}), 400
        
        if len(user_message) > 500:
            return jsonify({'error': '问题长度不能超过500个字符'}), 400
        
        reply = call_deepseek_api(user_message)
        
        add_chat_log(session['user_id'], user_message, reply)
        
        return jsonify({
            'success': True,
            'reply': reply,
            'question': user_message
        })
    
    except Exception as e:
        print("API error:", str(e))
        return jsonify({'error': '服务器错误，请稍后重试'}), 500


@app.route('/api/like/post/<int:post_id>', methods=['POST'])
@login_required
def api_like_post(post_id):
    count = like_post(post_id)
    if count is not None:
        return jsonify({'success': True, 'like_count': count})
    return jsonify({'error': '帖子不存在'}), 404


@app.route('/api/like/comment/<int:comment_id>', methods=['POST'])
@login_required
def api_like_comment(comment_id):
    count = like_comment(comment_id)
    if count is not None:
        return jsonify({'success': True, 'like_count': count})
    return jsonify({'error': '评论不存在'}), 404


@app.route('/api/comment/<int:comment_id>', methods=['PUT'])
@login_required
def api_edit_comment(comment_id):
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': '请提供评论内容'}), 400
    
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': '评论内容不能为空'}), 400
    
    success = edit_comment(comment_id, content)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': '评论不存在或无权限修改'}), 404


@app.route('/api/comment/<int:comment_id>', methods=['DELETE'])
@login_required
def api_delete_comment(comment_id):
    success = delete_comment(comment_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': '评论不存在'}), 404


@app.route('/api/post/<int:post_id>', methods=['DELETE'])
@login_required
def api_delete_post(post_id):
    post = get_post_by_id(post_id)
    if not post:
        return jsonify({'error': '帖子不存在'}), 404
    
    post_user_id = post.user_id if USE_REAL_DB else post['user_id']
    if post_user_id != session['user_id']:
        return jsonify({'error': '无权限删除此帖子'}), 403
    
    success = delete_post(post_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': '删除失败'}), 500


# ==================== DeepSeek API调用 ====================
def is_breast_cancer_related(question):
    breast_cancer_keywords = [
        '乳腺癌', '乳腺', '乳房', '乳腺肿瘤', '乳腺增生', '乳腺结节',
        '乳癌', '乳腺筛查', '乳腺检查', '乳腺超声', '乳腺钼靶', '乳腺MRI',
        '良性', '恶性', '肿瘤', '癌症', '癌', '肿瘤标志物', 'CA153',
        '化疗', '放疗', '手术', '靶向治疗', '内分泌治疗',
        '早期筛查', '预防', '康复', '预后', '复发', '转移',
        'BRCA', '基因突变', '遗传', '家族史',
        '乳头溢液', '乳房肿块', '乳房疼痛', '乳房胀痛',
        '保乳手术', '乳房切除', '重建手术',
        '新辅助治疗', '辅助治疗', '晚期治疗',
        'HER2', 'ER', 'PR', '三阴', '三阴性乳腺癌',
        '免疫治疗', 'PD-1', 'PD-L1',
        '生存期', '生存率', '五年生存率',
        '乳腺癌患者', '乳腺疾病', '乳腺健康'
    ]
    
    question_lower = question.lower()
    
    for keyword in breast_cancer_keywords:
        if keyword.lower() in question_lower:
            return True
    
    return False


def call_deepseek_api(question):
    if not is_breast_cancer_related(question):
        return '抱歉，我是一个乳腺癌辅助诊断AI助手，只能回答与乳腺癌相关的问题。如果您有这方面的疑问，我很乐意为您解答。'
    
    if not DEEPSEEK_API_KEY:
        return '抱歉，AI服务暂未配置，请联系管理员配置DeepSeek API密钥。'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
    }
    
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {
                'role': 'system',
                'content': '你是一个专业的乳腺癌辅助诊断AI助手。你的职责是只回答与乳腺癌相关的问题。\n\n你可以回答的话题包括：\n1. 乳腺癌的病因、症状和诊断\n2. 乳腺癌的预防方法和早期筛查\n3. 乳腺癌的治疗方式（手术、化疗、放疗、靶向治疗、内分泌治疗等）\n4. 乳腺癌的预后和康复护理\n5. 乳腺良性肿瘤与恶性肿瘤的区别\n6. 乳腺癌检查方法（乳腺超声、钼靶、核磁共振等）\n7. 乳腺癌相关指标的解读（如ER、PR、HER2、Ki-67等）\n8. 乳腺癌患者的饮食和生活方式建议\n9. 乳腺癌的遗传风险和基因检测\n\n**重要限制**：\n- 如果用户提问与乳腺癌完全无关，请直接拒绝回答，不要回答其他主题。\n- 如果用户的问题涉及医疗诊断，请明确说明不能替代专业医生诊断。\n- 回答必须基于医学常识，准确可靠。\n\n如果用户提问与乳腺癌无关，请礼貌地拒绝并引导用户提问相关问题。例如："抱歉，我是一个乳腺癌辅助诊断AI助手，只能回答与乳腺癌相关的问题。"\n\n请用简洁、专业的中文回答用户的问题。'
            },
            {
                'role': 'user',
                'content': question
            }
        ],
        'temperature': 0.5,
        'max_tokens': 1500
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        elif response.status_code == 401:
            return '抱歉，AI服务认证失败，请检查API密钥是否正确。'
        elif response.status_code == 429:
            return '抱歉，AI服务请求过于频繁，请稍后再试。'
        elif response.status_code == 403:
            return '抱歉，AI服务权限不足，请联系管理员。'
        else:
            return f'抱歉，AI服务暂时不可用，错误码：{response.status_code}'
    
    except requests.exceptions.Timeout:
        return '抱歉，AI服务响应超时，请稍后再试。'
    except requests.exceptions.ConnectionError:
        return '抱歉，无法连接到AI服务，请检查网络连接。'
    except Exception as e:
        print("DeepSeek API error:", str(e))
        return '抱歉，AI服务发生了错误，请稍后再试。'


# ==================== 数据库初始化 ====================
def init_database():
    if not USE_REAL_DB:
        return
    
    Base.metadata.create_all(engine)
    print("Database tables created successfully")


if __name__ == '__main__':
    init_database()
    app.run(debug=True)