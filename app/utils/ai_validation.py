import openai
import json
from config import Config

openai.api_key = Config.OPENAI_API_KEY

class QuestionValidator:
    def __init__(self):
        self.feedback_history = []
        self.depth_level = 1
        self.quality_threshold = 2.5  # Depth score threshold for acceptable questions
    
    def validate_question(self, question, context):
        validation_prompt = f"""
        Analyze the following question based on the context and provide a detailed evaluation:
        
        Context: 
        {context[:2000]}
        
        Question: {question['question']}
        Options: 
        A) {question['options']['A']}
        B) {question['options']['B']}
        C) {question['options']['C']}
        D) {question['options']['D']}
        Correct Answer: {question['answer']}
        
        Evaluation Criteria:
        1. Depth (1-3): Does the question test deep understanding beyond factual recall?
        2. Clarity: Is the question unambiguous?
        3. Distractor Quality: Are the incorrect options plausible?
        4. Relevance: Does the question relate directly to the context?
        5. Difficulty: Is the question appropriately challenging?
        
        Provide your evaluation in JSON format:
        {{
            "depth_score": float (1-3),
            "clarity_issues": [str],
            "distractor_issues": [str],
            "relevance_issues": [str],
            "difficulty_issues": [str],
            "overall_quality": "poor" | "fair" | "good" | "excellent",
            "suggested_improvement": str
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": validation_prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            evaluation = json.loads(response.choices[0].message['content'])
            return evaluation
        except Exception as e:
            print(f"Validation error: {e}")
            return {
                "depth_score": 1.0,
                "overall_quality": "poor",
                "error": str(e)
            }
    
    def improve_question(self, question, context, evaluation):
        # Adjust depth level based on feedback
        if evaluation.get('depth_score', 1.0) < self.quality_threshold:
            self.depth_level = min(3, self.depth_level + 0.5)
        
        improvement_prompt = f"""
        Improve the following question based on the evaluation and context:
        
        Original Question: {question['question']}
        Options: 
        A) {question['options']['A']}
        B) {question['options']['B']}
        C) {question['options']['C']}
        D) {question['options']['D']}
        Correct Answer: {question['answer']}
        
        Evaluation:
        {json.dumps(evaluation, indent=2)}
        
        Context:
        {context[:3000]}
        
        Improvement Guidelines:
        - Increase depth level to: {self.depth_level}
        - Address all issues identified in the evaluation
        - Maintain the core concept but enhance cognitive challenge
        - Ensure all options are plausible
        
        Provide the improved question in the same JSON format as the original:
        {{
            "question": str,
            "options": {{
                "A": str,
                "B": str,
                "C": str,
                "D": str
            }},
            "answer": str
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": improvement_prompt}],
                temperature=0.5,
                max_tokens=600
            )
            
            improved = json.loads(response.choices[0].message['content'])
            return improved
        except Exception as e:
            print(f"Improvement error: {e}")
            return question
    
    def process_feedback(self, feedback_text):
        """Process user feedback to adjust question generation parameters"""
        self.feedback_history.append(feedback_text)
        
        # Analyze feedback to adjust depth level
        analysis_prompt = f"""
        Analyze the following user feedback about quiz questions:
        {feedback_text}
        
        Determine if the feedback indicates questions are:
        - Too shallow/superficial
        - Too difficult/complex
        - Unrelated to content
        - Poorly worded
        
        Based on the analysis, suggest an adjustment to the question depth level (current: {self.depth_level}).
        Depth level ranges from 1 (basic) to 3 (advanced).
        
        Respond in JSON format:
        {{
            "analysis": str,
            "depth_adjustment": float (-0.5 to +0.5),
            "reasoning": str
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.4,
                max_tokens=300
            )
            
            feedback_analysis = json.loads(response.choices[0].message['content'])
            adjustment = feedback_analysis.get('depth_adjustment', 0)
            
            # Apply bounded adjustment
            self.depth_level = max(1, min(3, self.depth_level + adjustment))
            return feedback_analysis
        except Exception as e:
            print(f"Feedback processing error: {e}")
            return {"error": str(e)}