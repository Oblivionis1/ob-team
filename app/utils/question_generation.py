import openai
import re
import time
from config import Config

openai.api_key = Config.OPENAI_API_KEY

def generate_questions(text, num_questions=5, depth_level=1):
    prompt = f"""
    Generate {num_questions} challenging multiple-choice questions based on the text below.
    Each question must have 4 options (A-D) and indicate the correct answer.
    Questions should test deep understanding, not superficial facts.
    Depth level: {depth_level} (1=basic, 3=advanced)
    
    Text:
    {text[:3000]}... [truncated]
    
    Format:
    Question 1: [question text]
    A) [option A]
    B) [option B]
    C) [option C]
    D) [option D]
    Answer: [letter]
    """
    
    start_time = time.time()
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )
    
    if time.time() - start_time > 10:
        return generate_questions(text, num_questions, depth_level)  # Retry if timeout
    
    return parse_questions(response.choices[0].message['content'])

def parse_questions(raw_text):
    pattern = r"Question \d+: (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)\nAnswer: ([A-D])"
    matches = re.findall(pattern, raw_text, re.DOTALL)
    
    questions = []
    for match in matches:
        questions.append({
            "question": match[0].strip(),
            "options": {
                "A": match[1].strip(),
                "B": match[2].strip(),
                "C": match[3].strip(),
                "D": match[4].strip()
            },
            "answer": match[5].strip()
        })
    return questions

def validate_question(question, context):
    validation_prompt = f"""
    Validate the following question based on the context:
    Context: {context[:1000]}
    
    Question: {question['question']}
    Options: {question['options']}
    Answer: {question['answer']}
    
    Evaluation criteria:
    1. Does the question test deep understanding? (not factual recall)
    2. Is the correct answer unambiguous?
    3. Are distractors plausible but incorrect?
    
    Return JSON: {{"valid": bool, "issues": [str], "depth_score": 1-3}}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": validation_prompt}],
        temperature=0.3,
        max_tokens=500
    )
    
    return eval(response.choices[0].message['content'])