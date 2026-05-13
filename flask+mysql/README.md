# Flask + MySQL 学生管理系统

## 📁 项目结构

```
flask+mysql/
├── app.py              # Flask主程序（含路由和数据模型）
├── requirements.txt    # Python依赖包
├── init.sql            # MySQL数据库初始化脚本
├── README.md           # 说明文档（本文件）
└── templates/          # HTML模板文件夹
    ├── base.html       # 基础模板
    ├── index.html      # 学生列表页
    ├── add.html        # 添加学生页
    └── edit.html       # 编辑学生页
```

---

## 🚀 5分钟快速启动

### 第一步：安装Python依赖

打开命令行（CMD或PowerShell），进入项目目录：

```bash
cd C:\Users\86198\Desktop\flask+mysql
pip install -r requirements.txt
```

如果pip较慢，可使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 第二步：配置MySQL连接

打开 `app.py`，找到第15行的数据库配置：

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:你的密码@localhost:3306/student_db'
```

**修改说明：**
- `root` → 你的MySQL用户名
- `你的密码` → 你的MySQL密码
- `3306` → MySQL端口号（默认3306）
- `student_db` → 数据库名（可自行修改）

**修改示例（如果你的密码是123456）：**
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/student_db'
```

### 第三步：创建MySQL数据库

在MySQL命令行或Navicat中执行：

```sql
CREATE DATABASE IF NOT EXISTS student_db DEFAULT CHARACTER SET utf8mb4;
```

或直接执行项目中的 `init.sql` 文件。

### 第四步：启动Flask应用

```bash
cd C:\Users\86198\Desktop\flask+mysql
python app.py
```

### 第五步：打开浏览器访问

在浏览器中输入地址：`http://127.0.0.1:5000`

---

## 🎯 功能演示清单

| 功能 | 访问方式 |
|------|----------|
| 查看所有学生 | 访问 http://127.0.0.1:5000 |
| 添加学生 | 点击「添加学生」按钮或访问 /add |
| 编辑学生 | 点击学生行的「编辑」按钮 |
| 删除学生 | 点击学生行的「删除」按钮 |

---

## 📚 教学代码解读

### 1. 数据库连接配置（app.py 第14-16行）
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://用户名:密码@服务器:端口/数据库名'
db = SQLAlchemy(app)
```

### 2. 定义数据模型（app.py 第21-32行）
```python
class Student(db.Model):
    __tablename__ = 'students'  # 表名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
```

### 3. 增删改查操作

**增 (Create)**
```python
student = Student(name='张三', age=20)
db.session.add(student)
db.session.commit()
```

**查 (Read)**
```python
students = Student.query.all()  # 查询所有
student = Student.query.get(1)  # 按ID查询
```

**改 (Update)**
```python
student = Student.query.get(1)
student.age = 21
db.session.commit()
```

**删 (Delete)**
```python
student = Student.query.get(1)
db.session.delete(student)
db.session.commit()
```

### 4. 路由装饰器
```python
@app.route('/')                    # 首页
@app.route('/add', methods=['GET', 'POST'])  # 添加页（支持GET和POST）
@app.route('/edit/<int:student_id>')  # 编辑页（获取URL参数）
```

---

## ❓ 常见问题

### Q1: 提示 "ModuleNotFoundError: No module named 'flask'"
**解决：** 运行 `pip install -r requirements.txt`

### Q2: 提示 "Access denied for user 'root'"
**解决：** 检查 app.py 中的数据库密码是否正确

### Q3: 提示 "Unknown database 'student_db'"
**解决：** 先在MySQL中执行 `CREATE DATABASE student_db;`

### Q4: 网页显示乱码
**解决：** 确保数据库创建时使用 `utf8mb4` 字符集

### Q5: 如何让其他电脑访问？
**解决：** 将 `app.run(debug=True, port=5000)` 改为 `app.run(host='0.0.0.0', port=5000)`

---

## 🎓 教学建议

1. **先讲概念**：什么是ORM？为什么用它？
2. **演示流程**：让学生观察每一步操作对应的SQL语句
3. **对比教学**：展示纯SQL和ORM代码的对比
4. **鼓励实验**：让学生自己添加字段（如：班级、性别）

---

**祝教学顺利！🎉**
