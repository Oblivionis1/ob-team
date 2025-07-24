from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from database import db
from ..models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册页面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'audience')
        
        # 验证表单数据
        if not all([username, email, password, confirm_password]):
            flash('请填写所有必填字段', 'danger')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('两次密码不一致', 'danger')
            return render_template('auth/register.html')
            
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已被使用', 'danger')
            return render_template('auth/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'danger')
            return render_template('auth/register.html')
        
        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            role=role
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录页面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        if not all([username, password]):
            flash('请填写用户名和密码', 'danger')
            return render_template('auth/login.html')
        
        # 查找用户并验证密码
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('用户名或密码错误', 'danger')
            return render_template('auth/login.html')
        
        # 登录用户
        login_user(user, remember=remember)
        
        # 记录最后登录时间
        user.last_login = db.func.now()
        db.session.commit()
        
        # 重定向到下一页或主页
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功登出', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """用户个人资料页面"""
    return render_template('auth/profile.html')

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑用户资料"""
    if request.method == 'POST':
        email = request.form.get('email')
        bio = request.form.get('bio')
        
        # 验证邮箱是否已被使用
        if email != current_user.email and User.query.filter_by(email=email).first():
            flash('邮箱已被使用', 'danger')
            return render_template('auth/edit_profile.html')
        
        # 更新用户资料
        current_user.email = email
        current_user.bio = bio
        
        db.session.commit()
        
        flash('个人资料已更新', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html')

# 测试路由
@auth_bp.route('/test')
def test():
    return "认证系统正常运行" 