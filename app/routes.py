from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import db, create_app
from app.models import User, Presentation, Quiz, Response, Attendance, Comment
from app.forms import LoginForm, RegistrationForm, UploadForm, FeedbackForm
from app.utils.file_processing import extract_text
from app.utils.question_generation import generate_questions, validate_question
import os
from datetime import datetime
from config import Config

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,  # In production: generate_password_hash(form.password.data)
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # In production: check_password_hash
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'presenter':
        presentations = Presentation.query.filter_by(presenter_id=current_user.id).all()
    elif current_user.role == 'listener':
        attendances = Attendance.query.filter_by(user_id=current_user.id).all()
        presentations = [att.presentation for att in attendances]
    else:  # organizer
        presentations = Presentation.query.all()
    
    return render_template('dashboard.html', presentations=presentations)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.role not in ['presenter', 'organizer']:
        flash('Only presenters and organizers can upload content', 'danger')
        return redirect(url_for('dashboard'))
    
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        file_type = filename.split('.')[-1].lower()
        content = extract_text(file_path, file_type)
        
        presentation = Presentation(
            title=form.title.data,
            content=content,
            presenter_id=current_user.id
        )
        db.session.add(presentation)
        db.session.commit()
        
        # Generate quizzes
        quizzes = generate_questions(content, num_questions=5)
        for q in quizzes:
            quiz = Quiz(
                question=q['question'],
                options=q['options'],
                answer=q['answer'],
                presentation_id=presentation.id
            )
            db.session.add(quiz)
        db.session.commit()
        
        flash('Presentation uploaded and quizzes generated!', 'success')
        return redirect(url_for('presentation', id=presentation.id))
    
    return render_template('upload.html', form=form)

@app.route('/presentation/<int:id>')
@login_required
def presentation(id):
    pres = Presentation.query.get_or_404(id)
    return render_template('presentation.html', presentation=pres)

@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user already responded
    response = Response.query.filter_by(
        user_id=current_user.id, 
        quiz_id=quiz.id
    ).first()
    
    form = FeedbackForm()
    if request.method == 'POST' and not response:
        answer = request.form.get('answer')
        feedback_type = request.form.get('feedback_type')
        comment = request.form.get('comment')
        
        response = Response(
            user_id=current_user.id,
            quiz_id=quiz.id,
            answer=answer,
            feedback={"type": feedback_type, "comment": comment} if comment else None
        )
        db.session.add(response)
        db.session.commit()
        flash('Response recorded!', 'success')
        return redirect(url_for('quiz_results', quiz_id=quiz.id))
    
    return render_template('quiz.html', quiz=quiz, form=form, responded=bool(response))

@app.route('/quiz/<int:quiz_id>/results')
@login_required
def quiz_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    responses = Response.query.filter_by(quiz_id=quiz.id).all()
    
    # Calculate statistics
    total = len(responses)
    correct = sum(1 for r in responses if r.answer == quiz.answer)
    accuracy = (correct / total) * 100 if total > 0 else 0
    
    # User ranking
    user_correct = sum(1 for r in current_user.responses if r.answer == r.quiz.answer)
    user_total = len(current_user.responses)
    user_accuracy = (user_correct / user_total) * 100 if user_total > 0 else 0
    
    # 修复这里的 f-string 语法错误
    user_ranking = f"Top {max(10, int((100 - user_accuracy) // 10))}%"
    
    return render_template('results.html', 
                           quiz=quiz, 
                           accuracy=accuracy,
                           total=total,
                           user_accuracy=user_accuracy,
                           user_ranking=user_ranking)

@app.route('/reports/<int:pres_id>')
@login_required
def reports(pres_id):
    presentation = Presentation.query.get_or_404(pres_id)
    quizzes = presentation.quizzes
    
    # Calculate presentation stats
    stats = []
    for quiz in quizzes:
        responses = Response.query.filter_by(quiz_id=quiz.id).all()
        total = len(responses)
        correct = sum(1 for r in responses if r.answer == quiz.answer)
        incorrect = total - correct
        stats.append({
            'quiz_id': quiz.id,
            'question': quiz.question,
            'accuracy': (correct / total) * 100 if total > 0 else 0,
            'participation': f"{total}/{len(presentation.attendees)}",
            'correct': correct,
            'incorrect': incorrect
        })
    
    # Feedback analysis
    feedback_types = {'presenter': {}, 'question': {}, 'environment': {}}
    for quiz in quizzes:
        for response in quiz.responses:
            if response.feedback:
                ftype = response.feedback.get('type')
                comment = response.feedback.get('comment')
                if ftype in feedback_types:
                    feedback_types[ftype][comment] = feedback_types[ftype].get(comment, 0) + 1
    
    return render_template('reports.html', 
                          presentation=presentation,
                          stats=stats,
                          feedback=feedback_types)

# 添加讨论区功能路由
@app.route('/quiz/<int:quiz_id>/comment', methods=['POST'])
@login_required
def add_comment(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    comment_content = request.form.get('comment')
    
    if not comment_content:
        return jsonify(success=False, error="Comment cannot be empty")
    
    comment = Comment(
        content=comment_content,
        user_id=current_user.id,
        quiz_id=quiz.id
    )
    db.session.add(comment)
    db.session.commit()
    
    return jsonify(
        success=True,
        username=current_user.username,
        comment=comment_content
    )

@app.route('/quiz/<int:quiz_id>/comments')
@login_required
def get_comments(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    comments = [{
        'id': c.id,
        'content': c.content,
        'timestamp': c.timestamp.strftime('%Y-%m-%d %H:%M'),
        'username': c.user.username
    } for c in quiz.comments]
    
    return jsonify(comments)

if __name__ == '__main__':
    app.run(debug=True)