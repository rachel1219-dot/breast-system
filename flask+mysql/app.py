"""
Flask + MySQL 学生管理系统 - 最简教学示例
功能：增删改查学生的姓名和年龄
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# ==================== 1. 创建Flask应用 ====================
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # flash消息需要密钥

# ==================== 2. 配置MySQL数据库 ====================
# 格式: mysql+pymysql://用户名:密码@服务器地址:端口/数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Ljy042641@localhost:3306/student_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 创建数据库操作对象
db = SQLAlchemy(app)


# ==================== 3. 定义数据模型（相当于建表） ====================
class Student(db.Model):
    """学生表模型"""
    __tablename__ = 'students'  # 表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    name = db.Column(db.String(50), nullable=False)  # 姓名，不能为空
    age = db.Column(db.Integer, nullable=False)  # 年龄
    created_at = db.Column(db.DateTime, default=datetime.now)  # 创建时间

    def __repr__(self):
        return f'<Student {self.name}, {self.age}岁>'


# ==================== 4. 创建数据库（第一次运行时自动执行） ====================
with app.app_context():
    db.create_all()
    # 使用inspect检查表是否存在
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    if 'students' in tables:
        print("✅ 数据库表创建成功！")
    else:
        print("❌ 建表失败，请检查数据库连接配置")


# ==================== 5. 定义路由（URL规则） ====================

@app.route('/')
def index():
    """首页 - 显示所有学生"""
    students = Student.query.all()  # 查询所有学生
    return render_template('index.html', students=students)


@app.route('/add', methods=['GET', 'POST'])
def add_student():
    """添加学生"""
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')

        # 基本验证
        if not name or not age:
            flash('姓名和年龄不能为空！', 'error')
            return redirect(url_for('add_student'))

        try:
            age = int(age)
            if age < 1 or age > 150:
                flash('年龄范围应为1-150', 'error')
                return redirect(url_for('add_student'))
        except ValueError:
            flash('年龄必须是数字！', 'error')
            return redirect(url_for('add_student'))

        # 添加到数据库
        student = Student(name=name, age=age)
        db.session.add(student)
        db.session.commit()
        flash(f'学生 {name} 添加成功！', 'success')
        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    """编辑学生信息"""
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.name = request.form.get('name')
        student.age = request.form.get('age')
        db.session.commit()
        flash(f'学生信息更新成功！', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', student=student)


@app.route('/delete/<int:student_id>')
def delete_student(student_id):
    """删除学生"""
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f'学生 {student.name} 已删除', 'success')
    return redirect(url_for('index'))


# ==================== 6. 启动服务器 ====================
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🎓 Flask + MySQL 学生管理系统")
    print("=" * 50)
    print("📍 访问地址: http://127.0.0.1:5000")
    print("📝 按 Ctrl+C 停止服务器")
    print("=" * 50 + "\n")
    app.run(debug=True, port=5000)
