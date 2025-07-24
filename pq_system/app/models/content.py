from datetime import datetime
import os
from database import db

class Content(db.Model):
    """内容模型：存储上传的各种格式的内容"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_type = db.Column(db.String(20), nullable=False)  # 'text', 'ppt', 'pdf', 'audio', 'video'
    original_filename = db.Column(db.String(100))
    file_path = db.Column(db.String(255))
    processed_text = db.Column(db.Text)  # 处理后的文本内容
    processing_status = db.Column(db.String(20), default='pending')  # 'pending', 'processing', 'completed', 'failed'
    processing_error = db.Column(db.Text)  # 处理过程中的错误信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    questions = db.relationship('Question', backref='content', lazy='dynamic')
    quizzes = db.relationship('Quiz', backref='content', lazy='dynamic')
    
    def __repr__(self):
        return f'<Content {self.id}: {self.title}>'
    
    def to_dict(self):
        """转换为字典表示"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content_type': self.content_type,
            'original_filename': self.original_filename,
            'processing_status': self.processing_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'creator_id': self.creator_id
        }

class Quiz(db.Model):
    """Quiz model for organizing questions from content"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    time_limit = db.Column(db.Integer)  # Time limit in seconds (if any)
    start_time = db.Column(db.DateTime)  # When the quiz becomes available
    end_time = db.Column(db.DateTime)  # When the quiz stops accepting responses
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with questions in this quiz
    quiz_questions = db.relationship('QuizQuestion', backref='quiz', lazy='dynamic')
    
    def __repr__(self):
        return f'<Quiz {self.title}>'
        
class QuizQuestion(db.Model):
    """Junction table linking quizzes with questions with specific ordering"""
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)  # Order of questions in the quiz
    
    def __repr__(self):
        return f'<QuizQuestion {self.id}>' 