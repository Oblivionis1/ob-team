import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# 创建Flask应用
app = Flask(__name__, template_folder='app/templates')
app.config['SECRET_KEY'] = 'simple-dev-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///simple.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化SQLAlchemy
db = SQLAlchemy(app)

# 初始化LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 用户模型
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 加载用户回调
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 首页路由
@app.route('/')
def index():
    return render_template('simple_index.html')

# 测试路由
@app.route('/test')
def test():
    return jsonify({"status": "success", "message": "App is working!"})

# 注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'user')
        
        # 简单验证
        if not username or not email or not password:
            flash('请填写所有必填字段。', 'danger')
            return render_template('auth/simple_register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不匹配。', 'danger')
            return render_template('auth/simple_register.html')
        
        # 检查用户名或邮箱是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已被使用。', 'danger')
            return render_template('auth/simple_register.html')
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被使用。', 'danger')
            return render_template('auth/simple_register.html')
        
        # 创建新用户
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('您的账户已创建！现在可以登录了。', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/simple_register.html')

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # 通过邮箱查找用户
        user = User.query.filter_by(email=email).first()
        
        # 检查用户是否存在且密码是否正确
        if not user or not user.check_password(password):
            flash('邮箱或密码无效。', 'danger')
            return render_template('auth/simple_login.html')
        
        # 登录用户
        login_user(user, remember=remember)
        
        # 重定向到请求的页面或首页
        next_page = request.args.get('next')
        if not next_page or '://' in next_page:
            next_page = url_for('index')
        
        flash('您已成功登录！', 'success')
        return redirect(next_page)
    
    return render_template('auth/simple_login.html')

# 注销路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已注销。', 'info')
    return redirect(url_for('index'))

# 创建所有表格
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 