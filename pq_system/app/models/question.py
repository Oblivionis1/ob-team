from datetime import datetime
from database import db

class Question(db.Model):
    """问题模型：存储生成的题目"""
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)  # 题目解析
    difficulty = db.Column(db.String(20), default='medium')  # 'easy', 'medium', 'hard'
    quality_score = db.Column(db.Float, default=0.0)  # AI评估的题目质量分数
    feedback_score = db.Column(db.Float, default=0.0)  # 用户评分的平均分数
    generated_by = db.Column(db.String(50), default='ai')  # 'ai' or 'human'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    options = db.relationship('Option', backref='question', cascade="all, delete-orphan", lazy='dynamic')
    discussions = db.relationship('Discussion', backref='question', lazy='dynamic')
    
    def __repr__(self):
        return f'<Question {self.id}>'
    
    def get_correct_option(self):
        """获取正确选项"""
        return Option.query.filter_by(question_id=self.id, is_correct=True).first()
    
    def to_dict(self, include_answer=False):
        """转换为字典表示"""
        result = {
            'id': self.id,
            'text': self.text,
            'difficulty': self.difficulty,
            'options': [option.to_dict(include_answer) for option in self.options]
        }
        if include_answer:
            result['explanation'] = self.explanation
        return result

class Option(db.Model):
    """选项模型：存储问题的选项"""
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    # responses = db.relationship('QuizResponse', backref='selected_option', lazy='dynamic')  # 移除此行，改在 quiz.py 中定义
    
    def __repr__(self):
        return f'<Option {self.id}: {"Correct" if self.is_correct else "Incorrect"}>'
    
    def to_dict(self, include_answer=False):
        """转换为字典表示"""
        result = {
            'id': self.id,
            'text': self.text
        }
        if include_answer:
            result['is_correct'] = self.is_correct
        return result

class Discussion(db.Model):
    """讨论模型：存储关于问题的讨论"""
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 用户关系
    user = db.relationship('User', backref='discussions')
    
    # 回复关系
    parent_id = db.Column(db.Integer, db.ForeignKey('discussion.id'))
    replies = db.relationship(
        'Discussion', 
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f'<Discussion {self.id}>' 