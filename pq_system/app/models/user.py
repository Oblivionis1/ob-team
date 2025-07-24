from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from database import db

# 组织者-讲师关系表
organizer_presenter = db.Table('organizer_presenter',
    db.Column('organizer_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('presenter_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# 讲师-听众关系表
presenter_audience = db.Table('presenter_audience',
    db.Column('presenter_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('audience_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model, UserMixin):
    """用户模型：表示系统用户"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'organizer', 'presenter', 'audience'
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系
    # 创建的内容
    contents = db.relationship('Content', backref='creator', lazy='dynamic')
    
    # 创建的测验
    quizzes = db.relationship('Quiz', backref='creator', lazy='dynamic')
    
    # 组织者-讲师关系
    presenters = db.relationship(
        'User', 
        secondary=organizer_presenter,
        primaryjoin=(organizer_presenter.c.organizer_id == id),
        secondaryjoin=(organizer_presenter.c.presenter_id == id),
        backref=db.backref('organizers', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # 讲师-听众关系
    audiences = db.relationship(
        'User',
        secondary=presenter_audience,
        primaryjoin=(presenter_audience.c.presenter_id == id),
        secondaryjoin=(presenter_audience.c.audience_id == id),
        backref=db.backref('my_presenters', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # 反馈
    feedbacks = db.relationship('Feedback', backref='user', lazy='dynamic')
    
    # 测验回答 - 使用字符串引用解决循环依赖
    # responses = db.relationship('pq_system.app.models.quiz.QuizResponse', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """从纯文本密码生成密码哈希"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """检查提供的密码是否与存储的哈希匹配"""
        return check_password_hash(self.password_hash, password)
    
    def is_organizer(self):
        """检查用户是否是组织者"""
        return self.role == 'organizer'
    
    def is_presenter(self):
        """检查用户是否是讲师"""
        return self.role == 'presenter'
    
    def is_audience(self):
        """检查用户是否是听众"""
        return self.role == 'audience'
    
    def add_presenter(self, presenter):
        """组织者添加讲师"""
        if self.is_organizer() and presenter.is_presenter() and presenter not in self.presenters:
            self.presenters.append(presenter)
            return True
        return False
    
    def add_audience(self, audience):
        """讲师添加听众"""
        if self.is_presenter() and audience.is_audience() and audience not in self.audiences:
            self.audiences.append(audience)
            return True
        return False
    
    def to_dict(self):
        """转换为字典表示"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None
        }
        
    def __repr__(self):
        return f'<User {self.id}: {self.username} ({self.role})>' 