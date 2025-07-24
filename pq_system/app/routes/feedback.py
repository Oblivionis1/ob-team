from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from sqlalchemy import func

from database import db
from ..models.content import Content
from ..models.feedback import Feedback
from ..models.question import Question
from ..models.user import User

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

@feedback_bp.route('/')
def index():
    """反馈主页"""
    # 显示所有反馈
    feedbacks = Feedback.query.all()
    return render_template('feedback/presenter_index.html', feedbacks=feedbacks)

@feedback_bp.route('/create/<int:content_id>', methods=['GET', 'POST'])
def create(content_id):
    """创建反馈"""
    # 获取内容信息
    content = Content.query.get_or_404(content_id)
    
    if request.method == 'POST':
        feedback_type = request.form.get('feedback_type')
        comment = request.form.get('comment')
        
        # 使用管理员ID作为user_id
        user_id = 1  # 默认使用ID为1的管理员账户
        
        # 创建基本反馈对象
        feedback = Feedback(
            user_id=user_id,
            content_id=content_id,
            feedback_type=feedback_type,
            comment=comment
        )
        
        # 根据反馈类型设置特定字段
        if feedback_type == 'presenter':
            feedback.pace_rating = int(request.form.get('pace_rating', 3))
            feedback.clarity_rating = int(request.form.get('clarity_rating', 3))
            feedback.engagement_rating = int(request.form.get('engagement_rating', 3))
            
        elif feedback_type == 'question':
            question_id = request.form.get('question_id')
            if question_id:
                feedback.question_id = int(question_id)
                feedback.difficulty_rating = int(request.form.get('difficulty_rating', 3))
                feedback.relevance_rating = int(request.form.get('relevance_rating', 3))
                feedback.quality_rating = int(request.form.get('quality_rating', 3))
                
        elif feedback_type == 'environment':
            feedback.environment_rating = int(request.form.get('environment_rating', 3))
            feedback.audio_rating = int(request.form.get('audio_rating', 3))
            feedback.visual_rating = int(request.form.get('visual_rating', 3))
        
        # 保存反馈
        db.session.add(feedback)
        db.session.commit()
        
        flash('感谢您的反馈！', 'success')
        return redirect(url_for('content.view', id=content_id))
    
    # 获取与内容相关的问题，用于问题反馈
    questions = Question.query.filter_by(content_id=content_id).all()
    
    return render_template(
        'feedback/create.html', 
        content=content, 
        questions=questions
    )

@feedback_bp.route('/view/<int:id>')
def view(id):
    """查看特定反馈"""
    feedback = Feedback.query.get_or_404(id)
    content = Content.query.get_or_404(feedback.content_id)
    
    return render_template('feedback/view.html', feedback=feedback, content=content)

@feedback_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """删除反馈"""
    feedback = Feedback.query.get_or_404(id)
    
    db.session.delete(feedback)
    db.session.commit()
    
    flash('反馈已删除！', 'success')
    return redirect(url_for('feedback.index'))

@feedback_bp.route('/analytics/<int:content_id>')
def analytics(content_id):
    """查看反馈统计数据"""
    content = Content.query.get_or_404(content_id)
    
    # 获取所有反馈
    feedbacks = Feedback.query.filter_by(content_id=content_id).all()
    
    # 按类型分组反馈
    presenter_feedbacks = [f for f in feedbacks if f.feedback_type == 'presenter']
    question_feedbacks = [f for f in feedbacks if f.feedback_type == 'question']
    environment_feedbacks = [f for f in feedbacks if f.feedback_type == 'environment']
    
    # 计算平均评分
    presenter_stats = calculate_presenter_stats(presenter_feedbacks)
    environment_stats = calculate_environment_stats(environment_feedbacks)
    
    # 获取问题评分
    question_stats = calculate_question_stats(content_id)
    
    return render_template(
        'feedback/analytics.html',
        content=content,
        presenter_stats=presenter_stats,
        environment_stats=environment_stats,
        question_stats=question_stats,
        feedback_count=len(feedbacks)
    )

@feedback_bp.route('/api/presenter/<int:content_id>')
def api_presenter_feedback(content_id):
    """API: 获取讲师反馈数据"""
    content = Content.query.get_or_404(content_id)
    
    presenter_feedbacks = Feedback.query.filter_by(content_id=content_id, feedback_type='presenter').all()
    stats = calculate_presenter_stats(presenter_feedbacks)
    
    return jsonify(stats)

@feedback_bp.route('/api/questions/<int:content_id>')
def api_question_feedback(content_id):
    """API: 获取问题反馈数据"""
    content = Content.query.get_or_404(content_id)
    
    stats = calculate_question_stats(content_id)
    
    return jsonify(stats)

def calculate_presenter_stats(feedbacks):
    """计算讲师反馈统计数据"""
    if not feedbacks:
        return {
            'pace_avg': 0,
            'clarity_avg': 0,
            'engagement_avg': 0,
            'count': 0
        }
    
    pace_sum = sum(f.pace_rating for f in feedbacks if f.pace_rating)
    clarity_sum = sum(f.clarity_rating for f in feedbacks if f.clarity_rating)
    engagement_sum = sum(f.engagement_rating for f in feedbacks if f.engagement_rating)
    
    count = len(feedbacks)
    
    return {
        'pace_avg': round(pace_sum / count, 1) if count else 0,
        'clarity_avg': round(clarity_sum / count, 1) if count else 0,
        'engagement_avg': round(engagement_sum / count, 1) if count else 0,
        'count': count
    }

def calculate_environment_stats(feedbacks):
    """计算环境反馈统计数据"""
    if not feedbacks:
        return {
            'environment_avg': 0,
            'audio_avg': 0,
            'visual_avg': 0,
            'count': 0
        }
    
    env_sum = sum(f.environment_rating for f in feedbacks if f.environment_rating)
    audio_sum = sum(f.audio_rating for f in feedbacks if f.audio_rating)
    visual_sum = sum(f.visual_rating for f in feedbacks if f.visual_rating)
    
    count = len(feedbacks)
    
    return {
        'environment_avg': round(env_sum / count, 1) if count else 0,
        'audio_avg': round(audio_sum / count, 1) if count else 0,
        'visual_avg': round(visual_sum / count, 1) if count else 0,
        'count': count
    }

def calculate_question_stats(content_id):
    """计算问题反馈统计数据"""
    # 获取内容相关的所有问题
    questions = Question.query.filter_by(content_id=content_id).all()
    
    results = []
    for question in questions:
        # 获取问题的反馈
        feedbacks = Feedback.query.filter_by(question_id=question.id).all()
        
        if not feedbacks:
            stats = {
                'question_id': question.id,
                'question_text': question.text,
                'difficulty_avg': 0,
                'relevance_avg': 0,
                'quality_avg': 0,
                'count': 0
            }
        else:
            difficulty_sum = sum(f.difficulty_rating for f in feedbacks if f.difficulty_rating)
            relevance_sum = sum(f.relevance_rating for f in feedbacks if f.relevance_rating)
            quality_sum = sum(f.quality_rating for f in feedbacks if f.quality_rating)
            
            count = len(feedbacks)
            
            stats = {
                'question_id': question.id,
                'question_text': question.text,
                'difficulty_avg': round(difficulty_sum / count, 1) if count else 0,
                'relevance_avg': round(relevance_sum / count, 1) if count else 0,
                'quality_avg': round(quality_sum / count, 1) if count else 0,
                'count': count
            }
        
        results.append(stats)
    
    return results 