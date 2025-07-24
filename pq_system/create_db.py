import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入所有模型，确保它们被注册到SQLAlchemy
from app.models.user import User
from app.models.content import Content
from app.models.question import Question, Option, Discussion
from app.models.feedback import Feedback
from app.models.quiz import Quiz, QuizQuestion, QuizResponse

# 创建Flask应用
from flask import Flask
from database import db
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pq_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

with app.app_context():
    # 打印数据库路径
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    db_path = db_uri.replace('sqlite:///', '')
    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
    logging.info(f"数据库绝对路径: {abs_path}")
    
    # 确保表存在
    db.create_all()
    logging.info("数据库表已创建")
    
    # 检查是否已有用户
    if User.query.filter_by(username='admin').first() is None:
        # 创建基本用户
        admin = User(
            username='admin',
            email='admin@example.com',
            role='organizer',
            password_hash=generate_password_hash('admin123')
        )
        
        teacher = User(
            username='teacher',
            email='teacher@example.com',
            role='presenter',
            password_hash=generate_password_hash('teacher123')
        )
        
        student = User(
            username='student',
            email='student@example.com',
            role='audience',
            password_hash=generate_password_hash('student123')
        )
        
        # 添加到数据库
        db.session.add(admin)
        db.session.add(teacher)
        db.session.add(student)
        db.session.commit()
        
        logging.info("已成功创建示例用户:")
        logging.info("管理员: admin/admin123")
        logging.info("教师: teacher/teacher123") 
        logging.info("学生: student/student123")
    else:
        logging.info("数据库已存在，用户已创建")

logging.info("数据库初始化完成!") 