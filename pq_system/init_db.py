import os
import sys

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from app.models.user import User
from app.models.content import Content
from app.models.question import Question, Option, Discussion
from app.models.feedback import Feedback
from app.models.quiz import Quiz, QuizQuestion, QuizResponse

# 创建应用并初始化数据库
app = create_app('development')

# 打印出数据库路径，帮助调试
db_uri = app.config['SQLALCHEMY_DATABASE_URI']
print(f"使用的数据库URI: {db_uri}")
if db_uri.startswith('sqlite:///'):
    db_path = db_uri.replace('sqlite:///', '')
    if not db_path.startswith('/'):
        # 相对路径，打印完整路径
        abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
        print(f"数据库绝对路径: {abs_path}")

with app.app_context():
    # 删除所有表并重新创建
    db.drop_all()
    db.create_all()
    
    # 创建示例用户
    admin = User(
        username='admin',
        email='admin@example.com',
        role='organizer'
    )
    admin.set_password('admin123')
    
    teacher = User(
        username='teacher',
        email='teacher@example.com',
        role='presenter'
    )
    teacher.set_password('teacher123')
    
    student = User(
        username='student',
        email='student@example.com',
        role='audience'
    )
    student.set_password('student123')
    
    # 添加用户到数据库
    db.session.add(admin)
    db.session.add(teacher)
    db.session.add(student)
    db.session.commit()
    
    print("数据库初始化完成，已创建示例用户：")
    print("管理员: admin/admin123")
    print("教师: teacher/teacher123")
    print("学生: student/student123") 