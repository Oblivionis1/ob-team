from app import create_app, db
from app.models import User, Presentation, Quiz, Response, Attendance, Comment
from config import Config
from flask_migrate import Migrate
import os

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Presentation': Presentation,
        'Quiz': Quiz,
        'Response': Response,
        'Attendance': Attendance,
        'Comment': Comment
    }

@app.cli.command("seed")
def seed_database():
    """Seed the database with sample data for demonstration"""
    from datetime import datetime
    from werkzeug.security import generate_password_hash
    
    print("Seeding database...")
    
    # Create sample users
    organizer = User(
        username="org_admin",
        email="org@example.com",
        password=generate_password_hash("password123"),
        role="organizer"
    )
    
    presenter = User(
        username="presenter_john",
        email="john@example.com",
        password=generate_password_hash("password123"),
        role="presenter"
    )
    
    listeners = []
    for i in range(1, 4):
        listener = User(
            username=f"listener{i}",
            email=f"listener{i}@example.com",
            password=generate_password_hash("password123"),
            role="listener"
        )
        listeners.append(listener)
        db.session.add(listener)
    
    db.session.add(organizer)
    db.session.add(presenter)
    
    # Create sample presentation
    presentation = Presentation(
        title="Python Programming Fundamentals",
        content="""
        Python is a high-level, interpreted programming language known for its simplicity and readability.
        Key features include:
        - Dynamic typing
        - Automatic memory management
        - Extensive standard library
        - Support for multiple programming paradigms
        
        Python is widely used in:
        - Web development (Django, Flask)
        - Data science and machine learning (NumPy, Pandas, Scikit-learn)
        - Automation and scripting
        - Scientific computing
        
        This presentation covers:
        1. Basic syntax and data types
        2. Control structures (if-else, loops)
        3. Functions and modules
        4. Object-oriented programming concepts
        5. Error handling with exceptions
        """,
        presenter=presenter,
        timestamp=datetime.utcnow()
    )
    db.session.add(presentation)
    
    # Add attendees
    for listener in listeners:
        attendance = Attendance(user=listener, presentation=presentation)
        db.session.add(attendance)
    
    # Create sample quizzes
    quizzes = [
        {
            "question": "Which of the following is NOT a characteristic of Python?",
            "options": {
                "A": "Statically typed",
                "B": "Interpreted language",
                "C": "Supports multiple paradigms",
                "D": "Automatic memory management"
            },
            "answer": "A"
        },
        {
            "question": "What is the primary purpose of Python's 'if __name__ == \"__main__\":' statement?",
            "options": {
                "A": "To define the main class",
                "B": "To indicate the entry point of a program",
                "C": "To check if a module is being run directly",
                "D": "To import external libraries"
            },
            "answer": "C"
        },
        {
            "question": "Which Python data structure is mutable and unordered?",
            "options": {
                "A": "Tuple",
                "B": "List",
                "C": "Dictionary",
                "D": "String"
            },
            "answer": "C"
        }
    ]
    
    for i, quiz_data in enumerate(quizzes):
        quiz = Quiz(
            question=quiz_data["question"],
            options=quiz_data["options"],
            answer=quiz_data["answer"],
            presentation=presentation
        )
        db.session.add(quiz)
    
    # Create sample responses
    answers = ["A", "B", "C"]
    for i, listener in enumerate(listeners):
        for j, quiz in enumerate(presentation.quizzes):
            response = Response(
                user=listener,
                quiz=quiz,
                answer=answers[(i+j) % 3],
                timestamp=datetime.utcnow()
            )
            db.session.add(response)
    
    db.session.commit()
    print("Database seeded successfully!")

if __name__ == '__main__':
    # Create upload directories if not exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.PROCESSED_FOLDER, exist_ok=True)
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)