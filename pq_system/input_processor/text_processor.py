import os
import logging
from typing import Dict, Any, Optional

def process_text(file_path: str) -> Dict[str, Any]:
    """
    处理文本文件并返回提取的文本内容
    
    Args:
        file_path: 文本文件的路径
        
    Returns:
        包含处理结果的字典，包括文本内容和元数据
    """
    result = {
        "success": False,
        "text": "",
        "metadata": {},
        "error": None
    }
    
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            result["error"] = f"文件不存在: {file_path}"
            return result
        
        # 检查文件扩展名
        _, ext = os.path.splitext(file_path)
        supported_extensions = ['.txt', '.md', '.rtf']
        if ext.lower() not in supported_extensions:
            result["error"] = f"不支持的文件格式: {ext}. 支持的格式: {', '.join(supported_extensions)}"
            return result
        
        # 根据文件扩展名选择适当的处理方法
        if ext.lower() == '.txt':
            text = _process_txt(file_path)
        elif ext.lower() == '.md':
            text = _process_markdown(file_path)
        elif ext.lower() == '.rtf':
            text = _process_rtf(file_path)
        
        # 获取文件元数据
        metadata = {
            "filename": os.path.basename(file_path),
            "size_bytes": os.path.getsize(file_path),
            "extension": ext.lower(),
            "word_count": len(text.split()),
            "char_count": len(text)
        }
        
        result["success"] = True
        result["text"] = text
        result["metadata"] = metadata
        
    except Exception as e:
        result["error"] = str(e)
        logging.error(f"处理文本文件失败: {str(e)}", exc_info=True)
    
    return result

def _process_txt(file_path: str) -> str:
    """
    处理.txt文件
    """
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        return file.read()

def _process_markdown(file_path: str) -> str:
    """
    处理.md文件，移除Markdown标记
    """
    try:
        import markdown
        import html2text
        
        # 读取Markdown文件
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            md_text = file.read()
        
        # 将Markdown转换为HTML
        html = markdown.markdown(md_text)
        
        # 将HTML转换为纯文本
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        converter.ignore_images = True
        converter.ignore_emphasis = True
        text = converter.handle(html)
        
        return text
    except ImportError:
        # 如果没有markdown库，使用简单的文本处理
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            return file.read()

def _process_rtf(file_path: str) -> str:
    """
    处理.rtf文件
    """
    try:
        from striprtf.striprtf import rtf_to_text
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            rtf_text = file.read()
        
        # 将RTF转换为纯文本
        plain_text = rtf_to_text(rtf_text)
        return plain_text
    except ImportError:
        # 如果没有striprtf库，返回警告
        return "警告：无法处理RTF文件，请安装striprtf库。" 