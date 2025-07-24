import os
import uuid
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for, jsonify, send_file
from werkzeug.utils import secure_filename

from database import db
from ..models.content import Content
from input_processor import process_input

content_bp = Blueprint('content', __name__, url_prefix='/content')

def allowed_file(filename, content_type=None):
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    
    if content_type:
        return ext in allowed_extensions.get(content_type, set())
    else:
        # 检查所有允许的扩展名
        for extensions in allowed_extensions.values():
            if ext in extensions:
                return True
        return False

def get_content_type_from_extension(filename):
    """根据文件扩展名确定内容类型"""
    if '.' not in filename:
        return None
    ext = filename.rsplit('.', 1)[1].lower()
    
    ext_to_type = {
        'txt': 'text', 'md': 'text', 'rtf': 'text',
        'pdf': 'pdf',
        'ppt': 'ppt', 'pptx': 'ppt',
        'mp3': 'audio', 'wav': 'audio', 'ogg': 'audio', 'flac': 'audio',
        'mp4': 'video', 'avi': 'video', 'mov': 'video', 'mkv': 'video'
    }
    
    return ext_to_type.get(ext)

@content_bp.route('/')
def index():
    """列出用户的内容"""
    # 管理员身份，显示所有内容
    contents = Content.query.all()
    return render_template('content/index.html', contents=contents)

@content_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """上传新内容"""
    if request.method == 'POST':
        # 检查请求是否包含文件
        if 'file' not in request.files:
            flash('没有选择文件', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        title = request.form.get('title')
        description = request.form.get('description')
        content_type = request.form.get('content_type')
        
        # 验证表单字段
        if not title:
            flash('标题不能为空', 'danger')
            return redirect(request.url)
        
        # 如果未指定内容类型，尝试从文件扩展名确定
        if not content_type:
            content_type = get_content_type_from_extension(file.filename)
            if not content_type:
                flash('无法确定内容类型，请手动选择', 'danger')
                return redirect(request.url)
        
        # 如果用户没有选择文件，浏览器也会提交一个没有文件名的空部分
        if file.filename == '':
            flash('没有选择文件', 'danger')
            return redirect(request.url)
        
        if not allowed_file(file.filename, content_type):
            flash('所选内容类型不允许上传此类文件', 'danger')
            return redirect(request.url)
        
        # 使用安全的文件名并添加唯一标识符
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # 确保上传目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存文件
        file.save(file_path)
        
        # 创建新的内容记录（使用admin ID作为creator_id）
        creator_id = 1  # 默认使用ID为1的管理员账户
        
        # 创建新的内容记录
        content = Content(
            title=title,
            description=description,
            creator_id=creator_id,
            content_type=content_type,
            original_filename=filename,
            file_path=file_path,
            processing_status='pending'
        )
        
        db.session.add(content)
        db.session.commit()
        
        # 开始后台处理
        try:
            # 调用内容处理器
            result = process_input(file_path, content_type)
            
            if result.get('success', False):
                # 更新内容记录
                content.processed_text = result.get('text', '')
                content.processing_status = 'completed'
                db.session.commit()
                
                flash('内容已成功上传并处理！', 'success')
            else:
                # 处理失败
                content.processing_status = 'failed'
                content.processing_error = result.get('error', '未知错误')
                db.session.commit()
                
                flash(f'处理文件时出错: {content.processing_error}', 'warning')
        except Exception as e:
            # 捕获处理过程中的异常
            content.processing_status = 'failed'
            content.processing_error = str(e)
            db.session.commit()
            
            flash(f'处理文件时出现异常: {str(e)}', 'danger')
        
        return redirect(url_for('content.view', id=content.id))
    
    return render_template('content/upload.html')

@content_bp.route('/<int:id>')
def view(id):
    """查看内容详情"""
    content = Content.query.get_or_404(id)
    
    return render_template('content/view.html', content=content)

@content_bp.route('/<int:id>/download')
def download(id):
    """下载原始文件"""
    content = Content.query.get_or_404(id)
    
    if not os.path.exists(content.file_path):
        flash('文件不存在', 'danger')
        return redirect(url_for('content.view', id=content.id))
    
    return send_file(
        content.file_path, 
        as_attachment=True,
        download_name=content.original_filename
    )

@content_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """编辑内容详情"""
    content = Content.query.get_or_404(id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title:
            flash('标题不能为空', 'danger')
            return render_template('content/edit.html', content=content)
        
        # 更新内容
        content.title = title
        content.description = description
        db.session.commit()
        
        flash('内容已成功更新！', 'success')
        return redirect(url_for('content.view', id=content.id))
    
    return render_template('content/edit.html', content=content)

@content_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """删除内容"""
    content = Content.query.get_or_404(id)
    
    # 删除文件（如果存在）
    if content.file_path and os.path.exists(content.file_path):
        os.remove(content.file_path)
    
    # 从数据库中删除内容
    db.session.delete(content)
    db.session.commit()
    
    flash('内容已成功删除！', 'success')
    return redirect(url_for('content.index'))

@content_bp.route('/<int:id>/reprocess', methods=['POST'])
def reprocess(id):
    """重新处理内容"""
    content = Content.query.get_or_404(id)
    
    # 检查文件是否存在
    if not content.file_path or not os.path.exists(content.file_path):
        flash('原始文件不存在，无法重新处理。', 'danger')
        return redirect(url_for('content.view', id=content.id))
    
    # 更新状态
    content.processing_status = 'pending'
    content.processing_error = None
    db.session.commit()
    
    # 重新处理
    try:
        result = process_input(content.file_path, content.content_type)
        
        if result.get('success', False):
            content.processed_text = result.get('text', '')
            content.processing_status = 'completed'
            db.session.commit()
            
            flash('内容已成功重新处理！', 'success')
        else:
            content.processing_status = 'failed'
            content.processing_error = result.get('error', '未知错误')
            db.session.commit()
            
            flash(f'重新处理内容时出错: {content.processing_error}', 'warning')
    except Exception as e:
        content.processing_status = 'failed'
        content.processing_error = str(e)
        db.session.commit()
        
        flash(f'重新处理内容时出现异常: {str(e)}', 'danger')
    
    return redirect(url_for('content.view', id=content.id))

@content_bp.route('/<int:id>/text')
def get_text(id):
    """获取处理后的文本内容"""
    content = Content.query.get_or_404(id)
    
    if content.processing_status != 'completed':
        return jsonify({'error': '内容尚未完成处理'}), 400
    
    return jsonify({
        'id': content.id,
        'title': content.title,
        'text': content.processed_text,
        'processing_status': content.processing_status
    }) 