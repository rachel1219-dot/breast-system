# 乳腺癌智能诊断系统

**技术栈：** Flask + MySQL 8.0 + 随机森林 + DeepSeek API + Bootstrap 5

---

## ? 项目结构

```
breast-cancer-detection/
├── app.py                 # Flask 主后端（所有 API）
├── schema.sql             # MySQL 建表语句（6张表）
├── requirements.txt       # Python 依赖
├── .env                   # 环境配置（需填写数据库密码和API密钥）
├── start.bat              # Windows 一键启动脚本
├── rf_model.pkl           # 随机森林模型（首次运行自动生成）
├── scaler.pkl             # 数据标准化器（首次运行自动生成）
└── templates/
    ├── index.html         # 首页（乳腺癌科普）
    ├── auth.html          # 登录/注册页
    ├── dashboard.html     # 控制台
    ├── predict.html       # AI预测（30特征输入）
    ├── ai_chat.html       # DeepSeek AI咨询
    ├── community.html     # 交流中心
    ├── history.html       # 预测历史记录
    ├── medical.html       # 就医记录
    └── profile.html       # 个人中心
```

---

## ?? 部署步骤

### 1. 安装 MySQL 8.0

确保 MySQL 8.0 已安装并运行。

### 2. 初始化数据库

```sql
-- 在 MySQL 中执行：
source D:/code/breast-cancer-detection/schema.sql
```

或者：
```bash
mysql -u root -p < schema.sql
```

### 3. 配置 .env 文件

编辑 `.env` 文件，填写你的配置：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DB=breast_cancer_db

SECRET_KEY=your_secret_key_here

# DeepSeek API（可选，到 https://platform.deepseek.com 申请）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### 4. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

> ?? **mysqlclient 安装问题（Windows）：**
> 如果安装失败，可以改用 `PyMySQL`：
> ```bash
> pip install pymysql
> ```
> 然后在 `app.py` 顶部添加：
> ```python
> import pymysql
> pymysql.install_as_MySQLdb()
> ```

### 5. 启动服务

```bash
python app.py
```

或双击 `start.bat`

### 6. 访问系统

打开浏览器：**http://localhost:5000**

---

## ?? 数据库表结构

| 表名 | 说明 |
|------|------|
| `users` | 用户表（注册/登录） |
| `predictions` | 预测记录表（30特征+结果） |
| `ai_conversations` | AI对话记录表 |
| `medical_records` | 就医记录表 |
| `posts` | 交流帖子表 |
| `comments` | 帖子评论表 |
| `post_likes` | 点赞记录表 |

---

## ? 核心功能

| 功能 | 说明 |
|------|------|
| 注册/登录 | 密码 bcrypt 哈希，实时写入/查询 MySQL |
| 智能预测 | 随机森林（威斯康星数据集，准确率95%+），结果写库 |
| AI咨询 | DeepSeek API，对话历史持久化到 MySQL |
| 交流中心 | 发帖/评论/点赞，全部实时读写 MySQL |
| 就医记录 | CRUD 操作，实时同步数据库 |
| 个人中心 | 资料更新/密码修改，实时入库 |

---

## ? 常见问题

**Q: 启动报 `Access denied for user`**
A: 检查 `.env` 中的 `MYSQL_PASSWORD` 是否正确

**Q: 启动报 `Unknown database 'breast_cancer_db'`**
A: 先执行 `schema.sql` 建库

**Q: AI回复说"API密钥未配置"**
A: 这是正常的占位提示，在 `.env` 中填入真实 `DEEPSEEK_API_KEY` 即可

**Q: mysqlclient 安装失败**
A: 参考上方「安装 Python 依赖」部分的 PyMySQL 替代方案
