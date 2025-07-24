from datetime import datetime
from database import db

class Feedback(db.Model):
    """反馈模型：存储用户对演讲、题目、环境等的反馈"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    feedback_type = db.Column(db.String(20), nullable=False)  # 'presenter', 'question', 'environment'
    
    # 演讲者反馈
    pace_rating = db.Column(db.Integer)  # 1-5分，演讲速度评分（1太慢，3适中，5太快）
    clarity_rating = db.Column(db.Integer)  # 1-5分，清晰度评分
    engagement_rating = db.Column(db.Integer)  # 1-5分，吸引力评分
    
    # 题目反馈
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    difficulty_rating = db.Column(db.Integer)  # 1-5分，难度评分（1太简单，3适中，5太难）
    relevance_rating = db.Column(db.Integer)  # 1-5分，相关性评分
    quality_rating = db.Column(db.Integer)  # 1-5分，质量评分
    
    # 环境反馈
    environment_rating = db.Column(db.Integer)  # 1-5分，环境评分
    audio_rating = db.Column(db.Integer)  # 1-5分，音频质量评分
    visual_rating = db.Column(db.Integer)  # 1-5分，视觉效果评分
    
    # 通用字段
    comment = db.Column(db.Text)  # 反馈评论
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Feedback {self.id}: {self.feedback_type}>'
    
    def to_dict(self):
        """转换为字典表示"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'feedback_type': self.feedback_type,
            'comment': self.comment,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 根据反馈类型添加特定字段
        if self.feedback_type == 'presenter':
            result.update({
                'pace_rating': self.pace_rating,
                'clarity_rating': self.clarity_rating,
                'engagement_rating': self.engagement_rating
            })
        elif self.feedback_type == 'question':
            result.update({
                'question_id': self.question_id,
                'difficulty_rating': self.difficulty_rating,
                'relevance_rating': self.relevance_rating,
                'quality_rating': self.quality_rating
            })
        elif self.feedback_type == 'environment':
            result.update({
                'environment_rating': self.environment_rating,
                'audio_rating': self.audio_rating,
                'visual_rating': self.visual_rating
            })
            
        return result 