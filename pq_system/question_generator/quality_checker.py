import re
import logging
from typing import Dict, List, Any, Tuple
import requests
import time
import os
import sys

# 添加当前项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('quality_checker.log'),
        logging.StreamHandler()
    ]
)

class QuestionQualityChecker:
    """问题质量检查器：验证和改进生成的题目"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        """
        初始化质量检查器
        
        Args:
            api_key: API密钥，如果为None则从配置中获取
            model: 使用的AI模型
        """
        self.api_key = api_key or os.environ.get('DEEPSEEK_API_KEY') or config.get('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("未提供API密钥。请在配置中设置DEEPSEEK_API_KEY或直接提供api_key参数。")
        
        self.model = model
        self.api_base = "https://api.deepseek.com/v1"
    
    def check_questions(self, questions: List[Dict[str, Any]], original_text: str) -> List[Dict[str, Any]]:
        """
        检查题目质量并改进
        
        Args:
            questions: 待检查的问题列表
            original_text: 原始文本
            
        Returns:
            改进后的问题列表
        """
        if not questions:
            return []
        
        improved_questions = []
        
        for question in questions:
            # 对每个问题进行质量检查
            quality_score, issues = self._assess_question_quality(question, original_text)
            
            # 如果质量不达标，尝试改进
            if quality_score < 0.7 and issues:
                improved_question = self._improve_question(question, original_text, issues)
                if improved_question:
                    # 添加质量分数
                    improved_question["quality_score"] = quality_score
                    improved_questions.append(improved_question)
                else:
                    # 如果无法改进，保留原问题，但标记质量分数
                    question["quality_score"] = quality_score
                    improved_questions.append(question)
            else:
                # 质量足够好，保留原问题，添加质量分数
                question["quality_score"] = quality_score
                improved_questions.append(question)
        
        return improved_questions
    
    def _assess_question_quality(self, question: Dict[str, Any], original_text: str) -> Tuple[float, List[str]]:
        """
        评估问题质量
        
        Args:
            question: 待评估的问题
            original_text: 原始文本
            
        Returns:
            元组 (质量分数, 问题列表)
        """
        # 基本检查
        issues = []
        score = 1.0  # 起始满分
        
        # 1. 检查问题文本长度
        if len(question.get("question", "")) < 10:
            issues.append("问题文本太短")
            score -= 0.2
        
        # 2. 检查选项数量
        options = question.get("options", [])
        if len(options) != 4:
            issues.append(f"选项数量不正确（应为4个，实际为{len(options)}）")
            score -= 0.3
        
        # 3. 检查选项是否过于相似或过于简单
        if len(options) >= 2:
            similar_options = self._check_similar_options(options)
            if similar_options:
                issues.append(f"选项过于相似: {', '.join(similar_options)}")
                score -= 0.1
        
        # 4. 检查解析是否充分
        explanation = question.get("explanation", "")
        if len(explanation) < 20:
            issues.append("解析不充分")
            score -= 0.1
        
        # 5. 检查问题与原文相关性
        if not self._is_question_relevant(question, original_text):
            issues.append("问题与原文相关性低")
            score -= 0.3
        
        # 规范化分数在0-1之间
        score = max(0.0, min(1.0, score))
        
        return score, issues
    
    def _check_similar_options(self, options: List[str]) -> List[str]:
        """检查选项是否过于相似"""
        similar_options = []
        for i in range(len(options)):
            for j in range(i+1, len(options)):
                # 简单的相似度检查：如果两个选项有80%以上的词汇重叠
                words_i = set(re.findall(r'\b\w+\b', options[i].lower()))
                words_j = set(re.findall(r'\b\w+\b', options[j].lower()))
                
                if len(words_i) > 0 and len(words_j) > 0:
                    similarity = len(words_i.intersection(words_j)) / min(len(words_i), len(words_j))
                    if similarity > 0.8:
                        similar_options.append(f"选项{i+1}和选项{j+1}")
        
        return similar_options
    
    def _is_question_relevant(self, question: Dict[str, Any], original_text: str) -> bool:
        """检查问题与原文的相关性"""
        # 提取问题中的关键词
        question_text = question.get("question", "")
        question_words = set(re.findall(r'\b\w{4,}\b', question_text.lower()))
        
        # 如果问题中的关键词在原文中出现，认为相关
        for word in question_words:
            if word in original_text.lower():
                return True
        
        return False
    
    def _improve_question(self, question: Dict[str, Any], original_text: str, issues: List[str]) -> Dict[str, Any]:
        """
        改进问题质量
        
        Args:
            question: 待改进的问题
            original_text: 原始文本
            issues: 问题列表
            
        Returns:
            改进后的问题或None（如果无法改进）
        """
        # 构建提示词
        prompt = self._build_improvement_prompt(question, original_text, issues)
        
        try:
            # 调用API
            response = self._call_api(prompt)
            
            # 解析改进后的问题
            improved_question = self._parse_improved_question(response)
            
            if improved_question:
                return improved_question
            else:
                logging.warning("无法解析改进后的问题，返回原问题")
                return question
                
        except Exception as e:
            logging.error(f"改进问题时出错: {str(e)}", exc_info=True)
            return None
    
    def _build_improvement_prompt(self, question: Dict[str, Any], original_text: str, issues: List[str]) -> str:
        """构建改进提示词"""
        # 截取原文部分内容，避免提示词过长
        max_text_length = 1000
        if len(original_text) > max_text_length:
            text_excerpt = original_text[:max_text_length] + "..."
        else:
            text_excerpt = original_text
            
        prompt = f"""请改进以下选择题，解决这些问题：{', '.join(issues)}

原始文本内容（节选）：
{text_excerpt}

需要改进的题目：
问题：{question.get('question', '')}

选项：
A. {question.get('options', [''])[0] if len(question.get('options', [])) > 0 else ''}
B. {question.get('options', ['', ''])[1] if len(question.get('options', [])) > 1 else ''}
C. {question.get('options', ['', '', ''])[2] if len(question.get('options', [])) > 2 else ''}
D. {question.get('options', ['', '', '', ''])[3] if len(question.get('options', [])) > 3 else ''}

正确答案：{['A', 'B', 'C', 'D'][question.get('correct_option', 0)] if 0 <= question.get('correct_option', 0) < 4 else '未知'}

解析：{question.get('explanation', '')}

请提供改进后的问题，使用以下JSON格式：
```json
{{
  "question": "改进后的问题文本",
  "options": [
    "改进后的选项A",
    "改进后的选项B",
    "改进后的选项C",
    "改进后的选项D"
  ],
  "correct_option": 0,  // 正确答案的索引（0-3，对应A-D）
  "explanation": "详细的解析"
}}
```

请确保JSON格式正确，并且只输出JSON内容。"""
        
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
            "temperature": 0.5
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.RequestException as e:
            logging.error(f"API调用失败: {str(e)}")
            raise
    
    def _parse_improved_question(self, response: str) -> Dict[str, Any]:
        """解析改进后的问题"""
        try:
            # 从响应中提取JSON
            import json
            
            # 如果响应包含代码块，提取其中的JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response
            
            # 解析JSON
            question = json.loads(json_str)
            
            # 验证问题格式
            if not all(key in question for key in ["question", "options", "correct_option", "explanation"]):
                logging.warning(f"改进后的问题缺少必要字段: {question}")
                return None
            
            return question
            
        except Exception as e:
            logging.error(f"解析改进后的问题失败: {str(e)}", exc_info=True)
            return None
    
    def batch_check_questions(self, questions: List[Dict[str, Any]], original_text: str, 
                            batch_size: int = 5, delay: float = 1.0) -> List[Dict[str, Any]]:
        """
        批量检查和改进问题
        
        Args:
            questions: 待检查的问题列表
            original_text: 原始文本
            batch_size: 每批处理的问题数量
            delay: 批次间延迟（秒）
            
        Returns:
            改进后的问题列表
        """
        improved_questions = []
        
        # 按批次处理
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i+batch_size]
            
            # 检查并改进这一批问题
            improved_batch = self.check_questions(batch, original_text)
            improved_questions.extend(improved_batch)
            
            # 添加延迟，避免API请求过于频繁
            if i + batch_size < len(questions):
                time.sleep(delay)
        
        return improved_questions 