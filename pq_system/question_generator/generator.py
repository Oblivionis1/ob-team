import os
import logging
import json
import time
import random
from typing import List, Dict, Any, Optional
import requests
import sys

# 添加当前项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('question_generator.log'),
        logging.StreamHandler()
    ]
)

class QuestionGenerator:
    """问题生成器：基于内容生成选择题"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        """
        初始化问题生成器
        
        Args:
            api_key: API密钥，如果为None则从配置中获取
            model: 使用的AI模型
        """
        self.api_key = api_key or os.environ.get('DEEPSEEK_API_KEY') or config.get('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("未提供API密钥。请在配置中设置DEEPSEEK_API_KEY或直接提供api_key参数。")
        
        self.model = model
        self.api_base = "https://api.deepseek.com/v1"
    
    def generate_questions(self, text: str, num_questions: int = 5, difficulty: str = 'medium') -> List[Dict[str, Any]]:
        """
        生成指定数量的选择题
        
        Args:
            text: 基于此文本生成问题
            num_questions: 要生成的问题数量
            difficulty: 难度级别 ('easy', 'medium', 'hard')
            
        Returns:
            包含生成的问题的字典列表
        """
        if not text or len(text.strip()) < 50:
            raise ValueError("文本内容太短，无法生成有意义的问题")
        
        # 限制文本长度以避免超出模型限制
        max_text_length = 6000  # 安全限制
        if len(text) > max_text_length:
            logging.info(f"文本长度超过限制，截取前{max_text_length}个字符")
            text = text[:max_text_length]
        
        # 构建提示词
        prompt = self._build_prompt(text, num_questions, difficulty)
        
        try:
            # 调用AI API生成问题
            response = self._call_api(prompt)
            
            # 解析响应
            questions = self._parse_response(response)
            
            # 验证和清理问题
            questions = self._validate_questions(questions)
            
            return questions
        
        except Exception as e:
            logging.error(f"生成问题时出错: {str(e)}", exc_info=True)
            raise
    
    def _build_prompt(self, text: str, num_questions: int, difficulty: str) -> str:
        """构建提示词"""
        difficulty_descriptions = {
            'easy': "基础概念和直接事实，适合初学者",
            'medium': "中等难度，需要理解概念并应用知识",
            'hard': "高难度，需要深入理解和分析能力"
        }
        
        difficulty_desc = difficulty_descriptions.get(difficulty, difficulty_descriptions['medium'])
        
        prompt = f"""请基于以下内容，生成{num_questions}道高质量的四选一单选题。
难度要求：{difficulty}（{difficulty_desc}）

内容文本：
{text}

要求：
1. 每个问题必须与提供的文本内容直接相关
2. 每个问题必须有且仅有一个正确答案
3. 所有选项都应该合理且有干扰性
4. 提供每个问题的详细解析
5. 使用JSON格式输出，格式如下：
```json
[
  {{
    "question": "问题文本",
    "options": [
      "选项A",
      "选项B",
      "选项C",
      "选项D"
    ],
    "correct_option": 0,  // 正确答案的索引（0-3，对应A-D）
    "explanation": "解析说明"
  }},
  // ... 更多问题
]
```

请确保JSON格式正确，并且只输出JSON内容，不要有任何额外文本。"""
        
        return prompt
    
    def _call_api(self, prompt: str) -> str:
        """调用AI API"""
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.RequestException as e:
            logging.error(f"API调用失败: {str(e)}")
            raise
    
    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """解析API响应，提取JSON"""
        try:
            # 尝试从响应中提取JSON部分
            json_str = response
            
            # 如果响应包含代码块，提取其中的JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            
            # 解析JSON
            questions = json.loads(json_str)
            return questions
            
        except (json.JSONDecodeError, IndexError) as e:
            logging.error(f"解析响应失败: {str(e)}\n响应内容: {response}")
            raise ValueError(f"无法解析API返回的响应: {str(e)}")
    
    def _validate_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """验证和清理问题"""
        valid_questions = []
        
        for q in questions:
            # 检查必要字段
            if not all(key in q for key in ["question", "options", "correct_option", "explanation"]):
                logging.warning(f"跳过缺少必要字段的问题: {q}")
                continue
            
            # 验证选项和正确答案
            if not isinstance(q["options"], list) or len(q["options"]) != 4:
                logging.warning(f"跳过选项数量不正确的问题: {q}")
                continue
            
            if not isinstance(q["correct_option"], int) or q["correct_option"] not in range(4):
                logging.warning(f"跳过正确答案索引无效的问题: {q}")
                continue
            
            # 添加到有效问题列表
            valid_questions.append(q)
        
        return valid_questions
    
    def generate_questions_with_retry(self, text: str, num_questions: int = 5, difficulty: str = 'medium', 
                                     max_retries: int = 3) -> List[Dict[str, Any]]:
        """带有重试机制的问题生成"""
        retries = 0
        while retries < max_retries:
            try:
                return self.generate_questions(text, num_questions, difficulty)
            except Exception as e:
                logging.warning(f"生成问题失败 (尝试 {retries+1}/{max_retries}): {str(e)}")
                retries += 1
                time.sleep(2)  # 等待2秒后重试
        
        raise RuntimeError(f"在 {max_retries} 次尝试后仍无法生成问题") 