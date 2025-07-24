import os
import argparse
import sys
import logging

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from flask import render_template, redirect, url_for, Blueprint, session, g
from flask_login import login_user
from app.models.user import User
from database import db

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

# Create the application
app = create_app(os.getenv('FLASK_CONFIG', 'default'))

# 启用调试模式
app.debug = True

# Create main blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page route"""
    # 检查是否已经自动登录
    if not getattr(g, 'auto_login_done', False):
        return redirect(url_for('main.auto_login'))
    return render_template('index.html')

@main_bp.route('/start')
def start_using():
    """开始使用功能"""
    # 重定向到内容上传页面
    return redirect(url_for('content.upload'))

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard route"""
    # 检查是否已经自动登录
    if not getattr(g, 'auto_login_done', False):
        return redirect(url_for('main.auto_login'))
    return render_template('dashboard.html')

@main_bp.route('/auto-login')
def auto_login():
    """自动以管理员身份登录"""
    with app.app_context():
        # 获取管理员用户
        admin = User.query.filter_by(username='admin').first()
        if admin:
            # 登录管理员账号
            login_user(admin)
            # 设置标记，表示已经自动登录
            session['auto_login_done'] = True
            g.auto_login_done = True
            app.logger.info(f"自动登录成功: {admin.username}")
            return redirect(url_for('content.index'))
        else:
            app.logger.error("找不到管理员账号，请先运行初始化脚本")
            return "找不到管理员账号，请先运行初始化脚本 (simple_db.py)"

@app.before_request
def check_auto_login():
    """每个请求前检查是否自动登录"""
    g.auto_login_done = session.get('auto_login_done', False)

# Register the main blueprint
app.register_blueprint(main_bp)

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='PQ System')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()
    
    # Ensure upload and log directories exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)
    
    # Run the application
    app.run(host=args.host, port=args.port, debug=True) 