import os
import logging
from typing import Dict, Any, Optional

def process_pdf(file_path: str) -> Dict[str, Any]:
    """
    处理PDF文件并提取文本内容
    
    Args:
        file_path: PDF文件的路径
        
    Returns:
        包含处理结果的字典，包括提取的文本和元数据
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
        if ext.lower() != '.pdf':
            result["error"] = f"不支持的文件格式: {ext}. 仅支持PDF文件."
            return result
        
        # 提取PDF文本
        text, metadata = extract_text_from_pdf(file_path)
        
        # 获取文件元数据
        file_metadata = {
            "filename": os.path.basename(file_path),
            "size_bytes": os.path.getsize(file_path),
            "word_count": len(text.split()),
            "char_count": len(text)
        }
        
        # 合并PDF特定的元数据
        file_metadata.update(metadata)
        
        result["success"] = True
        result["text"] = text
        result["metadata"] = file_metadata
        
    except Exception as e:
        result["error"] = str(e)
        logging.error(f"处理PDF文件失败: {str(e)}", exc_info=True)
    
    return result

def extract_text_from_pdf(file_path: str) -> tuple:
    """
    从PDF文件中提取文本和元数据
    
    Returns:
        tuple: (文本内容, 元数据字典)
    """
    try:
        import PyPDF2
        
        text_content = []
        metadata = {}
        
        with open(file_path, 'rb') as file:
            # 创建PDF reader对象
            pdf_reader = PyPDF2.PdfReader(file)
            
            # 提取元数据
            if pdf_reader.metadata:
                metadata = {
                    "title": pdf_reader.metadata.get("/Title", ""),
                    "author": pdf_reader.metadata.get("/Author", ""),
                    "subject": pdf_reader.metadata.get("/Subject", ""),
                    "creator": pdf_reader.metadata.get("/Creator", ""),
                    "producer": pdf_reader.metadata.get("/Producer", ""),
                    "page_count": len(pdf_reader.pages)
                }
            else:
                metadata = {"page_count": len(pdf_reader.pages)}
            
            # 提取每一页的文本
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
        
        # 合并所有页面的文本
        full_text = "\n\n".join(text_content)
        
        return full_text, metadata
        
    except ImportError:
        logging.warning("未找到PyPDF2库，无法处理PDF文件。")
        return "需要安装PyPDF2库以处理PDF文件。", {}

def extract_text_with_ocr(file_path: str) -> str:
    """
    使用OCR从PDF中提取文本（用于扫描PDF文件）
    
    Args:
        file_path: PDF文件的路径
        
    Returns:
        提取的文本内容
    """
    try:
        import pytesseract
        from pdf2image import convert_from_path
        from PIL import Image
        
        # 将PDF转换为图像
        pages = convert_from_path(file_path, 300)  # DPI=300
        
        text_content = []
        
        # 对每个页面进行OCR处理
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page, lang='chi_sim+eng')  # 中文+英文
            text_content.append(text)
        
        # 合并所有页面的文本
        full_text = "\n\n".join(text_content)
        
        return full_text
        
    except ImportError:
        logging.warning("未找到OCR相关库，无法进行OCR处理。")
        return "需要安装pytesseract和pdf2image库以进行OCR处理。" 