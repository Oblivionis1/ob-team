from datetime import datetime
from database import db

class Quiz(db.Model):
    """测验模型：存储内容相关的测验信息"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    time_limit = db.Column(db.Integer)  # 时间限制（秒）
    start_time = db.Column(db.DateTime)  # 测验开始时间
    end_time = db.Column(db.DateTime)  # 测验结束时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    quiz_questions = db.relationship('QuizQuestion', backref='quiz', cascade="all, delete-orphan", lazy='dynamic')
    feedbacks = db.relationship('Feedback', backref='quiz', lazy='dynamic')
    
    @property
    def questions(self):
        """通过quiz_questions获取所有问题"""
        from .question import Question
        question_ids = [qq.question_id for qq in self.quiz_questions]
        return Question.query.filter(Question.id.in_(question_ids)).all()
    
    @property
    def status(self):
        """获取测验状态"""
        now = datetime.utcnow()
        if not self.is_active:
            return "inactive"
        elif self.start_time and now < self.start_time:
            return "scheduled"
        elif self.end_time and now > self.end_time:
            return "completed"
        else:
            return "active"
    
    def __repr__(self):
        return f'<Quiz {self.id}: {self.title}>'
    
    def to_dict(self, include_questions=False):
        """转换为字典表示"""
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content_id': self.content_id,
            'creator_id': self.creator_id,
            'is_active': self.is_active,
            'time_limit': self.time_limit,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if self.start_time:
            result['start_time'] = self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        if self.end_time:
            result['end_time'] = self.end_time.strftime('%Y-%m-%d %H:%M:%S')
        
        if include_questions:
            result['questions'] = [q.to_dict() for q in self.questions]
        
        return result


class QuizQuestion(db.Model):
    """测验问题关联：连接测验和问题"""
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    order = db.Column(db.Integer, default=0)  # 问题在测验中的顺序
    
    # 唯一约束确保问题在一个测验中不会重复
    __table_args__ = (db.UniqueConstraint('quiz_id', 'question_id'),)
    
    def __repr__(self):
        return f'<QuizQuestion {self.id}: Quiz {self.quiz_id} - Question {self.question_id}>'


class QuizResponse(db.Model):
    """测验响应：存储用户对测验问题的回答"""
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    response_time = db.Column(db.Float)  # 回答时间（秒）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系定义
    user = db.relationship('User', backref=db.backref('responses', lazy='dynamic'), foreign_keys=[user_id])
    question = db.relationship('Question', backref=db.backref('responses', lazy='dynamic'), foreign_keys=[question_id])
    selected_option = db.relationship('Option', backref=db.backref('responses', lazy='dynamic'), foreign_keys=[selected_option_id])
    
    def __repr__(self):
        return f'<QuizResponse {self.id}: {"Correct" if self.is_correct else "Incorrect"}>'
    
    def to_dict(self):
        """转换为字典表示"""
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'selected_option_id': self.selected_option_id,
            'is_correct': self.is_correct,
            'response_time': self.response_time,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } 