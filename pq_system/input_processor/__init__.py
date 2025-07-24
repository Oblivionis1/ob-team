import logging
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('input_processor.log'),
        logging.StreamHandler()
    ]
)

def process_input(file_path: str, content_type: str = None) -> Dict[str, Any]:
    """
    处理输入文件，自动识别文件类型或使用指定的内容类型
    
    Args:
        file_path: 输入文件的路径
        content_type: 可选，指定内容类型（'text', 'pdf', 'ppt', 'audio', 'video'）
        
    Returns:
        包含处理结果的字典，包括提取的文本和元数据
    """
    import os
    
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
        
        # 如果未指定内容类型，则根据文件扩展名自动确定
        if not content_type:
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            if ext in ['.txt', '.md', '.rtf']:
                content_type = 'text'
            elif ext == '.pdf':
                content_type = 'pdf'
            elif ext in ['.ppt', '.pptx']:
                content_type = 'ppt'
            elif ext in ['.mp3', '.wav', '.ogg', '.flac']:
                content_type = 'audio'
            elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
                content_type = 'video'
            else:
                result["error"] = f"未识别的文件类型: {ext}"
                return result
        
        # 根据内容类型调用相应的处理器
        if content_type == 'text':
            from .text_processor import process_text
            return process_text(file_path)
        elif content_type == 'pdf':
            from .pdf_processor import process_pdf
            return process_pdf(file_path)
        elif content_type == 'ppt':
            from .ppt_processor import process_ppt
            return process_ppt(file_path)
        elif content_type == 'audio':
            from .audio_processor import process_audio
            return process_audio(file_path)
        elif content_type == 'video':
            from .video_processor import process_video
            return process_video(file_path)
        else:
            result["error"] = f"不支持的内容类型: {content_type}"
            return result
    
    except Exception as e:
        result["error"] = str(e)
        logging.error(f"处理输入文件失败: {str(e)}", exc_info=True)
        return result 