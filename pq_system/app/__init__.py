import os
from flask import Flask
from flask_login import LoginManager
import logging

from config import config
from database import init_db

# Setup login manager for user authentication
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Set login view
login_manager.login_message_category = 'info'  # Set message category

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)
    
    # 使用config中的配置，而不是硬编码
    app_config = config[config_name]
    app.config.from_object(app_config)
    
    # 确保使用统一的数据库路径
    instance_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance'))
    db_path = os.path.join(instance_path, 'pq_system.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    logging.info(f"应用使用的数据库路径: {db_path}")
    
    # 确保instance目录存在
    os.makedirs(instance_path, exist_ok=True)
    
    # 设置文件上传配置
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload size
    app.config['ALLOWED_EXTENSIONS'] = {
        'text': {'txt', 'md', 'rtf'},
        'pdf': {'pdf'},
        'ppt': {'ppt', 'pptx'},
        'audio': {'mp3', 'wav', 'ogg', 'flac'},
        'video': {'mp4', 'avi', 'mov', 'mkv'}
    }
    
    # Create upload folder if it doesn't exist
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database
    init_db(app)
    
    # Initialize login manager
    login_manager.init_app(app)
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.content import content_bp
    from .routes.questions import questions_bp
    from .routes.feedback import feedback_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(feedback_bp)
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Load user callback for Flask-Login
    from .models.user import User
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app 