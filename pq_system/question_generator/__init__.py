import logging
from typing import Dict, List, Any, Optional
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('question_generator.log'),
        logging.StreamHandler()
    ]
)

from .generator import QuestionGenerator
from .quality_checker import QuestionQualityChecker

def generate_questions(content_text: str, num_questions: int = 5, difficulty: str = 'medium',
                       check_quality: bool = True) -> List[Dict[str, Any]]:
    """
    基于内容文本生成选择题
    
    Args:
        content_text: 内容文本
        num_questions: 要生成的问题数量
        difficulty: 难度级别 ('easy', 'medium', 'hard')
        check_quality: 是否检查并改进问题质量
        
    Returns:
        包含生成的问题的字典列表
    """
    try:
        # 获取API密钥
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            # 尝试从config中获取
            from dotenv import load_dotenv
            load_dotenv('exam.env')
            api_key = os.environ.get('DEEPSEEK_API_KEY')
            
        if not api_key:
            logging.error("找不到DEEPSEEK_API_KEY环境变量")
            return []
            
        # 创建问题生成器实例
        generator = QuestionGenerator(api_key=api_key)
        
        # 生成问题
        questions = generator.generate_questions_with_retry(
            text=content_text,
            num_questions=num_questions,
            difficulty=difficulty
        )
        
        # 如果需要检查质量
        if check_quality and questions:
            # 创建质量检查器实例
            checker = QuestionQualityChecker(api_key=api_key)
            
            # 检查并改进问题
            questions = checker.batch_check_questions(questions, content_text)
            
        return questions
        
    except Exception as e:
        logging.error(f"生成问题失败: {str(e)}", exc_info=True)
        return [] 