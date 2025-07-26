#!/usr/bin/env python3
"""
Test script to generate and save questions to the database
"""
import sys
import os
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv('exam.env')

from app import create_app
from app.models.content import Content
from app.models.question import Question, Option
from database import db

def create_sample_questions():
    """Create some sample questions for testing"""
    app = create_app()
    with app.app_context():
        # Get the first completed content
        content = Content.query.filter_by(processing_status='completed').first()
        if not content:
            print("No completed content found")
            return
        
        print(f"Creating sample questions for content: {content.title}")
        
        # Sample questions based on the PDF content about IT innovation
        sample_questions = [
            {
                "question": "根据文档内容，IT行业创新的主要特点是什么？",
                "options": [
                    "技术更新缓慢，变化较小",
                    "快速迭代，持续创新",
                    "只关注硬件发展",
                    "主要依赖传统方法"
                ],
                "correct_option": 1,
                "explanation": "IT行业以快速迭代和持续创新为主要特点，这是行业发展的核心驱动力。"
            },
            {
                "question": "在IT项目开发中，创新思维的重要性体现在哪里？",
                "options": [
                    "只需要按照既定流程执行",
                    "创新思维有助于解决复杂问题和提升效率",
                    "创新会增加项目风险，应该避免",
                    "创新只适用于大型企业"
                ],
                "correct_option": 1,
                "explanation": "创新思维在IT项目中能够帮助团队解决复杂问题，提升开发效率，是项目成功的关键因素。"
            },
            {
                "question": "根据文档描述，现代IT行业发展的趋势是什么？",
                "options": [
                    "回归传统开发模式",
                    "注重用户体验和敏捷开发",
                    "只关注技术本身",
                    "减少团队协作"
                ],
                "correct_option": 1,
                "explanation": "现代IT行业越来越注重用户体验，采用敏捷开发方法，强调快速响应和持续改进。"
            }
        ]
        
        # Save questions to database
        for q_data in sample_questions:
            question = Question(
                content_id=content.id,
                text=q_data['question'],
                explanation=q_data['explanation'],
                difficulty='medium',
                quality_score=0.8,
                generated_by='ai'
            )
            db.session.add(question)
            db.session.flush()  # Get the generated ID
            
            # Save options
            for i, option_text in enumerate(q_data['options']):
                option = Option(
                    question_id=question.id,
                    text=option_text,
                    is_correct=(i == q_data['correct_option'])
                )
                db.session.add(option)
        
        db.session.commit()
        print(f"Successfully created {len(sample_questions)} sample questions!")
        
        # Verify questions were saved
        total_questions = Question.query.count()
        print(f"Total questions in database: {total_questions}")

if __name__ == "__main__":
    create_sample_questions()