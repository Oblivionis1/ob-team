import os
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, abort
import json

from database import db
from ..models.content import Content
from ..models.question import Question, Option, Discussion
from ..models.user import User
from question_generator import generate_questions

questions_bp = Blueprint('questions', __name__, url_prefix='/questions')

@questions_bp.route('/')
def index():
    """列出所有问题"""
    # 获取所有问题
    questions = Question.query.all()
    # 获取所有内容
    contents = Content.query.all()
    return render_template('questions/index.html', questions=questions, contents=contents)

@questions_bp.route('/generate/<int:content_id>', methods=['GET', 'POST'])
def generate(content_id):
    """基于内容生成问题"""
    # 获取内容
    content = Content.query.get_or_404(content_id)
    
    # 检查内容是否已处理
    if content.processing_status != 'completed':
        flash('内容尚未处理完成，无法生成问题。', 'warning')
        return redirect(url_for('content.view', id=content_id))
    
    if request.method == 'POST':
        # 获取表单数据
        num_questions = int(request.form.get('num_questions', 5))
        difficulty = request.form.get('difficulty', 'medium')
        
        # 限制生成的问题数量
        num_questions = min(max(1, num_questions), 10)
        
        # 检查文本是否可用
        if not content.processed_text:
            flash('没有可用的文本内容用于生成问题。', 'danger')
            return redirect(url_for('content.view', id=content_id))
        
        try:
            # 调用问题生成器
            generated_questions = generate_questions(
                content_text=content.processed_text,
                num_questions=num_questions,
                difficulty=difficulty
            )
            
            if not generated_questions:
                flash('生成问题失败，请稍后再试。', 'danger')
                return redirect(url_for('content.view', id=content_id))
            
            # 保存生成的问题到数据库
            saved_questions = []
            for q in generated_questions:
                question = Question(
                    content_id=content_id,
                    text=q.get('question', ''),
                    explanation=q.get('explanation', ''),
                    difficulty=difficulty,
                    quality_score=q.get('quality_score', 0.0),
                    generated_by='ai'
                )
                db.session.add(question)
                db.session.flush()  # 获取生成的ID
                
                # 保存选项
                options = q.get('options', [])
                correct_idx = q.get('correct_option', 0)
                
                for i, option_text in enumerate(options):
                    option = Option(
                        question_id=question.id,
                        text=option_text,
                        is_correct=(i == correct_idx)
                    )
                    db.session.add(option)
                
                saved_questions.append(question)
            
            db.session.commit()
            
            flash(f'成功生成 {len(saved_questions)} 个问题！', 'success')
            return redirect(url_for('questions.content_questions', content_id=content_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'生成问题时出错: {str(e)}', 'danger')
            return redirect(url_for('content.view', id=content_id))
    
    return render_template('questions/generate.html', content=content)

@questions_bp.route('/content/<int:content_id>')
def content_questions(content_id):
    """查看特定内容的所有问题"""
    # 获取内容
    content = Content.query.get_or_404(content_id)
    
    # 获取与内容相关的所有问题
    questions = Question.query.filter_by(content_id=content_id).all()
    
    return render_template('questions/content_questions.html', content=content, questions=questions)

@questions_bp.route('/<int:id>')
def view(id):
    """查看问题详情"""
    question = Question.query.get_or_404(id)
    
    # 获取关联的内容
    content = Content.query.get_or_404(question.content_id)
    
    return render_template('questions/view.html', question=question, content=content)

@questions_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """编辑问题"""
    question = Question.query.get_or_404(id)
    
    # 获取关联的内容
    content = Content.query.get_or_404(question.content_id)
    
    # 获取问题的选项
    options = Option.query.filter_by(question_id=question.id).all()
    
    if request.method == 'POST':
        # 获取表单数据
        question_text = request.form.get('question_text')
        explanation = request.form.get('explanation')
        difficulty = request.form.get('difficulty')
        
        option_texts = [
            request.form.get('option1'),
            request.form.get('option2'),
            request.form.get('option3'),
            request.form.get('option4')
        ]
        
        correct_option = request.form.get('correct_option')
        if correct_option is not None:
            correct_option = int(correct_option)
        
        # 验证表单数据
        if not question_text or not all(option_texts) or correct_option is None:
            flash('请填写所有必填字段。', 'danger')
            return render_template('questions/edit.html', question=question, options=options)
        
        # 更新问题
        question.text = question_text
        question.explanation = explanation
        question.difficulty = difficulty
        question.generated_by = 'human'  # 标记为人工编辑过
        
        # 更新选项
        for i, option in enumerate(options):
            option.text = option_texts[i]
            option.is_correct = (i == correct_option)
        
        db.session.commit()
        
        flash('问题已成功更新！', 'success')
        return redirect(url_for('questions.view', id=question.id))
    
    return render_template('questions/edit.html', question=question, options=options)

@questions_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """删除问题"""
    question = Question.query.get_or_404(id)
    
    content_id = question.content_id
    
    # 删除问题及相关选项
    db.session.delete(question)  # 级联删除会处理选项
    db.session.commit()
    
    flash('问题已成功删除！', 'success')
    return redirect(url_for('questions.content_questions', content_id=content_id))

@questions_bp.route('/<int:id>/discussions')
def discussions(id):
    """查看问题的讨论"""
    question = Question.query.get_or_404(id)
    
    # 获取讨论列表
    discussions = Discussion.query.filter_by(question_id=question.id, parent_id=None).all()
    
    return render_template('questions/discussions.html', question=question, discussions=discussions)

@questions_bp.route('/<int:id>/discussions/add', methods=['POST'])
def add_discussion(id):
    """添加讨论"""
    question = Question.query.get_or_404(id)
    
    text = request.form.get('text')
    parent_id = request.form.get('parent_id')
    
    if not text:
        flash('讨论内容不能为空', 'danger')
        return redirect(url_for('questions.discussions', id=id))
    
    # 创建新讨论，使用admin ID作为user_id
    user_id = 1  # 默认使用ID为1的管理员账户
    
    # 创建新讨论
    discussion = Discussion(
        question_id=question.id,
        user_id=user_id,
        text=text,
        parent_id=parent_id if parent_id else None
    )
    
    db.session.add(discussion)
    db.session.commit()
    
    flash('讨论已添加！', 'success')
    return redirect(url_for('questions.discussions', id=id))

@questions_bp.route('/api/random', methods=['GET'])
def api_random():
    """API: 获取随机问题"""
    # 获取随机问题
    questions = Question.query.all()
    
    if not questions:
        return jsonify({'error': '没有可用的问题'}), 404
    
    # 从问题列表中随机选择一个
    import random
    question = random.choice(questions)
    
    # 获取选项，并混淆顺序
    options = Option.query.filter_by(question_id=question.id).all()
    options_data = [{'id': o.id, 'text': o.text} for o in options]
    random.shuffle(options_data)
    
    # 找出正确选项的新位置
    correct_option = Option.query.filter_by(question_id=question.id, is_correct=True).first()
    for i, o in enumerate(options_data):
        if o['id'] == correct_option.id:
            correct_index = i
            break
    
    return jsonify({
        'id': question.id,
        'text': question.text,
        'options': [o['text'] for o in options_data],
        'correct_index': correct_index
    }) 