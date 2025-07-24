from flask_sqlalchemy import SQLAlchemy
import os
import logging

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    # 输出数据库位置
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    logging.info(f"使用的数据库URI: {db_uri}")
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        if not db_path.startswith('/'):
            # 相对路径，打印完整路径
            abs_path = os.path.join(os.path.dirname(app.instance_path), db_path)
            logging.info(f"数据库绝对路径: {abs_path}")
            # 确保目录存在
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    # Create all tables if they don't exist
    with app.app_context():
        db.create_all()
        logging.info("数据库表已创建")
        
    return db 