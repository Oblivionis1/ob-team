from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'organizer', 'presenter', 'listener'
    presentations = db.relationship('Presentation', backref='presenter', lazy=True)
    responses = db.relationship('Response', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)  # 添加评论关系

class Presentation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    presenter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='presentation', lazy=True)
    attendees = db.relationship('Attendance', backref='presentation', lazy=True)
    feedback = db.Column(db.JSON, default={})  # 存储聚合后的反馈数据（修复缩进）

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)  # {A: "...", B: "...", C: "...", D: "..."}
    answer = db.Column(db.String(1), nullable=False)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentation.id'), nullable=False)
    responses = db.relationship('Response', backref='quiz', lazy=True)
    comments = db.relationship('Comment', backref='quiz', lazy=True)  # 添加评论关系

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    answer = db.Column(db.String(1), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.JSON, nullable=True)  # {type: "question", comment: "too shallow"}

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentation.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))