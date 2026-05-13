"""
Flask + MySQL 学生管理系统 - 接口文档生成器
使用 reportlab 生成 PDF 文档
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 注册中文字体
try:
    pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
    FONT_NAME = 'SimSun'
except:
    FONT_NAME = 'Helvetica'

# 创建PDF
doc = SimpleDocTemplate(
    "C:\\Users\\86198\\Desktop\\flask+mysql\\接口文档.pdf",
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm
)

# 样式定义
styles = getSampleStyleSheet()
accent_color = HexColor('#2A6B5A')

title_style = ParagraphStyle(
    'Title',
    parent=styles['Title'],
    fontName=FONT_NAME,
    fontSize=24,
    textColor=accent_color,
    spaceAfter=30,
    alignment=TA_CENTER
)

h1_style = ParagraphStyle(
    'H1',
    parent=styles['Heading1'],
    fontName=FONT_NAME,
    fontSize=18,
    textColor=accent_color,
    spaceBefore=20,
    spaceAfter=15,
    borderWidth=2,
    borderColor=accent_color,
    borderPadding=5
)

h2_style = ParagraphStyle(
    'H2',
    parent=styles['Heading2'],
    fontName=FONT_NAME,
    fontSize=14,
    textColor=accent_color,
    spaceBefore=15,
    spaceAfter=10
)

h3_style = ParagraphStyle(
    'H3',
    parent=styles['Heading3'],
    fontName=FONT_NAME,
    fontSize=12,
    textColor=HexColor('#333333'),
    spaceBefore=10,
    spaceAfter=8
)

body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontName=FONT_NAME,
    fontSize=10,
    spaceAfter=8,
    leading=14
)

code_style = ParagraphStyle(
    'Code',
    parent=styles['Code'],
    fontName='Courier',
    fontSize=8,
    spaceBefore=5,
    spaceAfter=5,
    leftIndent=10,
    backColor=HexColor('#f5f5f5'),
    borderColor=accent_color,
    borderWidth=2,
    borderPadding=8
)

# 构建文档内容
elements = []

# 封面
elements.append(Spacer(1, 3*cm))
elements.append(Paragraph("Flask + MySQL", title_style))
elements.append(Paragraph("学生管理系统", title_style))
elements.append(Spacer(1, 1*cm))
elements.append(Paragraph("接口文档 v1.0", ParagraphStyle('Subtitle', fontName=FONT_NAME, fontSize=14, alignment=TA_CENTER)))
elements.append(Spacer(1, 2*cm))
elements.append(Paragraph("适用对象：Web开发课程学生", ParagraphStyle('Info', fontName=FONT_NAME, fontSize=11, alignment=TA_CENTER)))
elements.append(Paragraph("版本日期：2026-04-28", ParagraphStyle('Info', fontName=FONT_NAME, fontSize=11, alignment=TA_CENTER)))
elements.append(PageBreak())

# 接口概览
elements.append(Paragraph("接口概览", h1_style))
elements.append(Paragraph("本接口文档描述学生管理系统的所有API端点，供前后端开发参考使用。", body_style))

overview_data = [
    ['接口名称', '请求方法', 'URL', '说明'],
    ['学生列表', 'GET', '/', '显示所有学生'],
    ['添加学生', 'GET/POST', '/add', '添加新学生'],
    ['编辑学生', 'GET/POST', '/edit/<id>', '编辑指定学生'],
    ['删除学生', 'GET', '/delete/<id>', '删除指定学生']
]
overview_table = Table(overview_data, colWidths=[3*cm, 2.5*cm, 4*cm, 4*cm])
overview_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), accent_color),
    ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
    ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f9f9f9')]),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
elements.append(overview_table)
elements.append(PageBreak())

# 1. 学生列表接口
elements.append(Paragraph("1. 学生列表接口", h1_style))
elements.append(Paragraph("基本信息", h2_style))

basic_info1 = [
    ['字段', '值'],
    ['接口名称', '学生列表'],
    ['请求方法', 'GET'],
    ['URL', '/'],
    ['返回格式', 'HTML页面']
]
basic_table1 = Table(basic_info1, colWidths=[3*cm, 5*cm])
basic_table1.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8e8e8')),
    ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
elements.append(basic_table1)
elements.append(Spacer(1, 0.5*cm))

elements.append(Paragraph("后端代码", h3_style))
elements.append(Paragraph("""<pre>
@app.route('/')
def index():
    \"\"\"首页 - 显示所有学生\"\"\"
    students = Student.query.all()  # 查询所有学生
    return render_template('index.html', students=students)
</pre>""", code_style))

elements.append(PageBreak())

# 2. 添加学生接口
elements.append(Paragraph("2. 添加学生接口", h1_style))
elements.append(Paragraph("基本信息", h2_style))

basic_info2 = [
    ['字段', '值'],
    ['接口名称', '添加学生'],
    ['请求方法', 'GET/POST'],
    ['URL', '/add'],
    ['Content-Type', 'application/x-www-form-urlencoded']
]
basic_table2 = Table(basic_info2, colWidths=[3*cm, 5*cm])
basic_table2.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8e8e8')),
    ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
elements.append(basic_table2)

elements.append(Spacer(1, 0.3*cm))
elements.append(Paragraph("请求参数", h2_style))
param_data = [
    ['参数名', '类型', '必填', '说明'],
    ['name', 'string', '是', '学生姓名，最大50字符'],
    ['age', 'integer', '是', '学生年龄，范围1-150']
]
param_table = Table(param_data, colWidths=[2.5*cm, 2*cm, 1.5*cm, 4*cm])
param_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8e8e8')),
    ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
elements.append(param_table)

elements.append(Spacer(1, 0.3*cm))
elements.append(Paragraph("后端代码", h2_style))
elements.append(Paragraph("""<pre>
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        # 创建并保存学生记录
        student = Student(name=name, age=age)
        db.session.add(student)
        db.session.commit()
        flash(f'学生 {name} 添加成功！', 'success')
        return redirect(url_for('index'))
    return render_template('add.html')
</pre>""", code_style))

elements.append(PageBreak())

# 3. 编辑学生接口
elements.append(Paragraph("3. 编辑学生接口", h1_style))
elements.append(Paragraph("基本信息", h2_style))

basic_info3 = [
    ['字段', '值'],
    ['接口名称', '编辑学生'],
    ['请求方法', 'GET/POST'],
    ['URL', '/edit/<student_id>'],
    ['参数类型', 'path (整数)']
]
basic_table3 = Table(basic_info3, colWidths=[3*cm, 5*cm])
basic_table3.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8e8e8')),
    ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
elements.append(basic_table3)

elements.append(Spacer(1, 0.3*cm))
elements.append(Paragraph("后端代码", h2_style))
elements.append(Paragraph("""<pre>
@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        student.name = request.form.get('name')
        student.age = request.form.get('age')
        db.session.commit()
        flash('学生信息更新成功！', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', student=student)
</pre>""", code_style))

elements.append(PageBreak())

# 4. 删除学生接口
elements.append(Paragraph("4. 删除学生接口", h1_style))
elements.append(Paragraph("基本信息", h2_style))

basic_info4 = [
    ['字段', '值'],
    ['接口名称', '删除学生'],
    ['请求方法', 'GET'],
    ['URL', '/delete/<student_id>'],
    ['注意', '建议使用POST或添加确认机制']
]
basic_table4 = Table(basic_info4, colWidths=[3*cm, 5*cm])
basic_table4.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8e8e8')),
    ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
elements.append(basic_table4)

elements.append(Spacer(1, 0.3*cm))
elements.append(Paragraph("后端代码", h2_style))
elements.append(Paragraph("""<pre>
@app.route('/delete/<int:student_id>')
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f'学生 {student.name} 已删除', 'success')
    return redirect(url_for('index'))
</pre>""", code_style))

elements.append(PageBreak())

# 5. 数据库模型
elements.append(Paragraph("5. 数据库模型", h1_style))
elements.append(Paragraph("Student 模型结构", h2_style))

model_data = [
    ['字段名', '类型', '约束', '说明'],
    ['id', 'Integer', 'PK, AUTO_INCREMENT', '主键'],
    ['name', 'String(50)', 'NOT NULL', '学生姓名'],
    ['age', 'Integer', 'NOT NULL', '学生年龄'],
    ['created_at', 'DateTime', 'DEFAULT NOW()', '创建时间']
]
model_table = Table(model_data, colWidths=[2.5*cm, 2.5*cm, 3.5*cm, 3*cm])
model_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8e8e8')),
    ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
elements.append(model_table)

elements.append(Spacer(1, 0.3*cm))
elements.append(Paragraph("模型代码", h2_style))
elements.append(Paragraph("""<pre>
class Student(db.Model):
    __tablename__ = 'students'  # 表名
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Student {self.name}, {self.age}岁>'
</pre>""", code_style))

elements.append(PageBreak())

# 6. 错误处理
elements.append(Paragraph("6. 错误处理", h1_style))

error_data = [
    ['HTTP状态码', '含义', '处理方式'],
    ['200', '请求成功', '正常返回页面或数据'],
    ['302', '重定向', '表单提交后跳转'],
    ['404', '资源不存在', '显示404页面'],
    ['500', '服务器错误', '显示500错误页面']
]
error_table = Table(error_data, colWidths=[3*cm, 3*cm, 5*cm])
error_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8e8e8')),
    ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
elements.append(error_table)

elements.append(Spacer(1, 0.5*cm))
elements.append(Paragraph("<b>提示：</b>实际生产环境中，建议使用 POST 方法处理删除操作，以防止CSRF攻击和误操作。", body_style))

# 生成PDF
doc.build(elements)
print("[OK] PDF generated successfully!")
print("Location: C:\\Users\\86198\\Desktop\\flask+mysql\\接口文档.pdf")
