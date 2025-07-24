import os
import logging
import tempfile
from typing import Dict, Any, List, Optional

def process_video(file_path: str) -> Dict[str, Any]:
    """
    处理视频文件并提取音频和文本内容
    
    Args:
        file_path: 视频文件的路径
        
    Returns:
        包含处理结果的字典，包括提取的文本和元数据
    """
    result = {
        "success": False,
        "text": "",
        "frames_with_text": [],
        "audio_text": "",
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
        supported_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        if ext.lower() not in supported_extensions:
            result["error"] = f"不支持的文件格式: {ext}. 支持的格式: {', '.join(supported_extensions)}"
            return result
        
        # 获取视频元数据
        metadata = extract_video_metadata(file_path)
        
        # 提取音频并进行语音转文本
        audio_text = extract_audio_from_video(file_path)
        
        # 提取视频帧并识别文本
        frames_with_text = extract_frames_with_text(file_path)
        
        # 合并所有文本内容
        all_text = [audio_text] if audio_text else []
        if frames_with_text:
            frame_texts = [frame["text"] for frame in frames_with_text if frame.get("text")]
            all_text.extend(frame_texts)
        
        combined_text = "\n\n".join([text for text in all_text if text])
        
        # 更新文件元数据
        file_metadata = {
            "filename": os.path.basename(file_path),
            "size_bytes": os.path.getsize(file_path),
            "format": ext.lower()[1:],
            "word_count": len(combined_text.split()) if combined_text else 0,
            "char_count": len(combined_text) if combined_text else 0
        }
        
        # 合并视频特定的元数据
        file_metadata.update(metadata)
        
        result["success"] = True
        result["text"] = combined_text
        result["audio_text"] = audio_text
        result["frames_with_text"] = frames_with_text
        result["metadata"] = file_metadata
        
    except Exception as e:
        result["error"] = str(e)
        logging.error(f"处理视频文件失败: {str(e)}", exc_info=True)
    
    return result

def extract_video_metadata(file_path: str) -> Dict[str, Any]:
    """
    提取视频文件的元数据
    
    Args:
        file_path: 视频文件路径
        
    Returns:
        包含视频元数据的字典
    """
    metadata = {}
    
    try:
        from moviepy.editor import VideoFileClip
        
        # 加载视频
        video = VideoFileClip(file_path)
        
        # 提取基本元数据
        metadata = {
            "duration_seconds": video.duration,
            "fps": video.fps,
            "width": video.w,
            "height": video.h,
            "aspect_ratio": round(video.w / video.h, 2) if video.h > 0 else None,
            "rotation": getattr(video, 'rotation', 0)
        }
        
        # 关闭视频
        video.close()
        
    except ImportError:
        logging.warning("未找到moviepy库，无法提取完整的视频元数据。")
    except Exception as e:
        logging.warning(f"提取视频元数据时出错: {str(e)}")
    
    return metadata

def extract_audio_from_video(file_path: str) -> str:
    """
    从视频中提取音频并进行语音识别
    
    Args:
        file_path: 视频文件路径
        
    Returns:
        识别的文本内容
    """
    try:
        from moviepy.editor import VideoFileClip
        import speech_recognition as sr
        
        # 创建临时文件用于保存提取的音频
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            
        # 加载视频并提取音频
        with VideoFileClip(file_path) as video:
            video.audio.write_audiofile(temp_path, logger=None)
        
        # 使用音频处理模块进行语音识别
        from .audio_processor import process_audio
        
        # 处理音频
        audio_result = process_audio(temp_path)
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        # 如果返回的是字典（增强版函数），提取文本
        if isinstance(audio_result, dict):
            return audio_result.get("text", "")
        # 如果返回的是字符串（旧版函数），直接返回
        return audio_result
        
    except ImportError:
        logging.warning("未找到必要的库，无法从视频中提取音频文本。")
        return "需要安装moviepy和SpeechRecognition库以从视频中提取音频。"
    except Exception as e:
        logging.error(f"从视频中提取音频时出错: {str(e)}", exc_info=True)
        return f"从视频中提取音频时出错: {str(e)}"

def extract_frames_with_text(file_path: str, interval: int = 10) -> List[Dict[str, Any]]:
    """
    从视频中提取帧并识别其中的文本（如幻灯片内容）
    
    Args:
        file_path: 视频文件路径
        interval: 帧提取间隔（秒）
        
    Returns:
        包含帧信息和识别文本的列表
    """
    frames = []
    
    try:
        import cv2
        import pytesseract
        import numpy as np
        from moviepy.editor import VideoFileClip
        
        # 加载视频
        video = VideoFileClip(file_path)
        duration = video.duration
        fps = video.fps
        
        # 每隔interval秒提取一帧
        for t in range(0, int(duration), interval):
            # 获取帧
            frame = video.get_frame(t)
            
            # 转换为OpenCV格式
            frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            
            # 转换为灰度图
            gray = cv2.cvtColor(frame_cv, cv2.COLOR_BGR2GRAY)
            
            # 应用自适应阈值处理，以提高OCR准确性
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # OCR识别文本
            text = pytesseract.image_to_string(thresh, lang='chi_sim+eng')
            
            # 如果识别到文本，保存帧信息
            if text and text.strip():
                frames.append({
                    "time": t,
                    "text": text.strip(),
                    "frame_number": int(t * fps)
                })
        
        # 关闭视频
        video.close()
        
    except ImportError:
        logging.warning("未找到必要的库，无法从视频中提取文本。")
    except Exception as e:
        logging.error(f"从视频中提取文本时出错: {str(e)}", exc_info=True)
    
    return frames 