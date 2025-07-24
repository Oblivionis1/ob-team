import sqlite3
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 数据库路径
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'pq_system.db'))
logging.info(f"使用数据库: {DB_PATH}")

# 确保目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 创建connection
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 创建用户表
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL,
    bio TEXT,
    avatar_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
''')

# 检查是否已有用户
cursor.execute('SELECT COUNT(*) FROM user WHERE username = ?', ('admin',))
if cursor.fetchone()[0] == 0:
    # 创建管理员用户
    from werkzeug.security import generate_password_hash
    
    # 插入用户
    users = [
        ('admin', 'admin@example.com', generate_password_hash('admin123'), 'organizer'),
        ('teacher', 'teacher@example.com', generate_password_hash('teacher123'), 'presenter'),
        ('student', 'student@example.com', generate_password_hash('student123'), 'audience'),
    ]
    
    cursor.executemany(
        'INSERT INTO user (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
        users
    )
    
    conn.commit()
    logging.info("已创建示例用户:")
    logging.info("admin/admin123 (组织者)")
    logging.info("teacher/teacher123 (讲师)")
    logging.info("student/student123 (听众)")
else:
    logging.info("用户表中已有数据")

conn.close()
logging.info("数据库初始化完成") 