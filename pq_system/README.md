# PQ System

PQ System is a comprehensive solution for generating quiz questions from educational content. It supports processing text, PowerPoint, PDF, audio, and video inputs to extract content and automatically generate multiple-choice questions for educational use.

## Features

1. **Input Processing**
   - Text file processing
   - PowerPoint file processing
   - PDF file processing
   - Audio file processing
   - Video file processing (includes both audio transcription and visual text extraction)

2. **Question Generation**
   - AI-powered multiple-choice question generation
   - Quality checking and improvement loop
   - Difficulty level selection
   - Support for various educational topics

3. **User Management**
   - Three user roles: Organizer, Presenter, and Audience
   - User registration and authentication
   - Role-based access control

4. **Quiz Management**
   - Create quizzes from processed content
   - Schedule quizzes with start and end times
   - Randomized question order
   - Option to prevent simple copying by randomizing option order

5. **Feedback System**
   - Question quality feedback
   - Presenter feedback
   - Environment feedback
   - Discussion forums for each question

6. **Analytics**
   - Quiz statistics for presenters and organizers
   - Individual performance analytics for audience members
   - Feedback analysis tools

## Installation

### Prerequisites

- Python 3.8+
- FFmpeg (for audio/video processing)
- Tesseract OCR (for text extraction from video frames)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/pq_system.git
cd pq_system
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the requirements:

```bash
pip install -r requirements.txt
```

4. Set up environment variables (create a `.env` file in the root directory):

```
FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
```

5. Initialize the database:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Usage

1. Start the application:

```bash
python main.py --debug
```

2. Access the web interface:
   - Open your browser and go to `http://localhost:5000`

3. Register as different user types:
   - Organizer: Create and manage events, monitor quizzes
   - Presenter: Upload content, create quizzes, view results
   - Audience: Take quizzes, provide feedback, participate in discussions

4. Upload content:
   - Log in as a presenter
   - Navigate to Content -> Upload
   - Select file and content type
   - Provide title and description

5. Generate questions:
   - View uploaded content
   - Select "Generate Questions"
   - Choose number of questions and difficulty

6. Create a quiz:
   - Select questions to include
   - Set quiz parameters
   - Publish the quiz

7. Take a quiz:
   - Log in as audience
   - Navigate to available quizzes
   - Answer questions and view results

## Project Structure

```
pq_system/
├── app/                       # Web application
│   ├── routes/                # API routes
│   ├── models/                # Database models
│   ├── static/                # Static files
│   └── templates/             # HTML templates
├── input_processor/           # Input processing module
├── question_generator/        # Question generation module
├── config.py                  # Configuration
├── database.py                # Database connection
└── main.py                    # Main application entry point
```

## Customization

- **OpenAI Model**: You can change the OpenAI model in `question_generator/generator.py` to use more advanced models like GPT-4 for better question quality
- **Question Quality Parameters**: Adjust threshold values in `question_generator/quality_checker.py` to change the strictness of quality checks
- **Input Processors**: Extend the input processing capabilities by modifying the modules in the `input_processor` directory

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 