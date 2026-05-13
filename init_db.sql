-- 乳腺癌辅助诊断系统数据库初始化脚本
-- 数据库名: breast_cancer_detection_db

-- 使用数据库
USE breast_cancer_detection_db;

-- 1. 用户表
CREATE TABLE IF NOT EXISTS user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    is_doctor BOOLEAN DEFAULT FALSE COMMENT '是否为医生',
    doctor_title VARCHAR(100) DEFAULT NULL COMMENT '医生职称',
    hospital VARCHAR(200) DEFAULT NULL COMMENT '所属医院'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 预测记录表
CREATE TABLE IF NOT EXISTS prediction (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    radius_mean FLOAT COMMENT '半径均值',
    texture_mean FLOAT COMMENT '纹理均值',
    perimeter_mean FLOAT COMMENT '周长均值',
    area_mean FLOAT COMMENT '面积均值',
    smoothness_mean FLOAT COMMENT '平滑度均值',
    compactness_mean FLOAT COMMENT '紧密度均值',
    concavity_mean FLOAT COMMENT '凹度均值',
    concave_points_mean FLOAT COMMENT '凹点均值',
    symmetry_mean FLOAT COMMENT '对称性均值',
    fractal_dimension_mean FLOAT COMMENT '分形维数均值',
    result VARCHAR(20) COMMENT '预测结果',
    probability FLOAT COMMENT '概率',
    prediction_time FLOAT COMMENT '预测耗时',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预测记录表';

-- 3. 聊天记录表
CREATE TABLE IF NOT EXISTS chat_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    question TEXT NOT NULL COMMENT '用户问题',
    answer TEXT NOT NULL COMMENT 'AI回答',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天记录表';

-- 4. 帖子表（交流中心）
CREATE TABLE IF NOT EXISTS post (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '发布用户ID',
    title VARCHAR(200) NOT NULL COMMENT '帖子标题',
    content TEXT NOT NULL COMMENT '帖子内容',
    post_type ENUM('patient', 'doctor') DEFAULT 'patient' COMMENT '帖子类型：patient-病友交流，doctor-医生科普',
    category VARCHAR(50) DEFAULT 'general' COMMENT '分类',
    view_count INT DEFAULT 0 COMMENT '浏览次数',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='帖子表';

-- 5. 就医记录表（个人中心）
CREATE TABLE IF NOT EXISTS medical_record (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    hospital VARCHAR(200) NOT NULL COMMENT '就诊医院',
    department VARCHAR(100) NOT NULL COMMENT '就诊科室',
    symptoms TEXT COMMENT '症状描述',
    diagnosis TEXT COMMENT '诊断结果',
    report_path VARCHAR(500) COMMENT '报告单文件路径',
    visit_date DATE NOT NULL COMMENT '就诊日期',
    doctor_name VARCHAR(50) COMMENT '医生姓名',
    notes TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='就医记录表';

-- 6. 评论表（帖子评论）
CREATE TABLE IF NOT EXISTS comment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    post_id INT NOT NULL COMMENT '帖子ID',
    user_id INT NOT NULL COMMENT '评论用户ID',
    content TEXT NOT NULL COMMENT '评论内容',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论表';

-- 插入示例数据
-- 示例用户
INSERT INTO user (username, password, is_doctor, doctor_title, hospital) VALUES 
('admin', 'admin123', TRUE, '主任医师', '北京协和医院'),
('test', 'test123', FALSE, NULL, NULL);

-- 示例帖子
INSERT INTO post (user_id, title, content, post_type, category) VALUES
(1, '乳腺癌早期筛查的重要性', '乳腺癌是女性最常见的恶性肿瘤之一，早期筛查可以大大提高治愈率。建议35岁以上女性每年进行一次乳腺检查...', 'doctor', '科普'),
(2, '术后康复经验分享', '大家好，我是去年做的乳腺癌手术，现在恢复得很好。想和大家分享一下我的康复经验...', 'patient', '经验分享');

-- 示例评论
INSERT INTO comment (post_id, user_id, content) VALUES
(1, 2, '感谢医生的科普！我妈妈就是早期发现做了手术，现在恢复得很好。'),
(1, 1, '早期筛查确实非常重要，建议大家都要重视。');

-- 示例就医记录
INSERT INTO medical_record (user_id, hospital, department, symptoms, diagnosis, visit_date, doctor_name) VALUES
(2, '北京协和医院', '乳腺外科', '乳房肿块，轻微疼痛', '乳腺良性结节', '2024-01-15', '张医生'),
(2, '北京协和医院', '乳腺外科', '定期复查', '恢复良好', '2024-04-15', '李医生');

-- 查看创建的表
SHOW TABLES;
