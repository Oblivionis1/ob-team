# PQ System Project Structure

```
pq_system/
├── app/                       # Web application
│   ├── __init__.py
│   ├── routes/                # API routes
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication routes
│   │   ├── content.py         # Content management routes
│   │   ├── questions.py       # Question routes
│   │   └── feedback.py        # Feedback routes
│   ├── models/                # Database models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   ├── content.py         # Content model
│   │   ├── question.py        # Question model
│   │   └── feedback.py        # Feedback model
│   ├── static/                # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/             # HTML templates
│       ├── auth/
│       ├── dashboard/
│       └── quiz/
├── input_processor/           # Input processing module
│   ├── __init__.py
│   ├── text_processor.py      # Process text files
│   ├── ppt_processor.py       # Process PowerPoint files
│   ├── pdf_processor.py       # Process PDF files
│   ├── audio_processor.py     # Process audio files
│   └── video_processor.py     # Process video files
├── question_generator/        # Question generation module
│   ├── __init__.py
│   ├── generator.py           # Generate questions
│   └── quality_checker.py     # Check question quality
├── config.py                  # Configuration
├── database.py                # Database connection
└── main.py                    # Main application entry point
``` 