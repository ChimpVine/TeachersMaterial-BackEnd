# Flask Education API

This project is a Flask-based API that provides a suite of educational tools including lesson plan generation, quiz creation, workbook generation, vocabulary list creation, rubric generation, and more. It is designed to assist educators in creating various teaching materials efficiently.

## Features

- **Lesson Plan Generation**: Generate lesson plans based on provided text and parameters.
- **Quiz Generator**: Create quizzes based on topic, language, difficulty, and other parameters.
- **Workbook Generation**: Generate workbooks from PDF content.
- **Worksheet Generation**: Create various types of educational worksheets like MCQs, fill-in-the-blanks, and sequencing questions.
- **Tongue Twister Creation**: Generate tongue twisters based on a specified topic.
- **Vocabulary List Generation**: Generate a list of vocabulary words based on the grade level, subject, and difficulty.
- **Rubric Generation**: Create grading rubrics based on assignment descriptions and other parameters.
- **Word Puzzle Creation**: Generate word puzzles based on the given topic.
- **YouTube Summarizer**: Summarize YouTube videos based on the provided URL.

## Prerequisites

- Python 3.x
- Flask
- Additional libraries listed in `requirements.txt`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   Create a `.env` file in the root directory and add the required environment variables:

   ```
   USER_EMAIL=your-email@example.com
   USER_PASSWORD=yourpassword
   ```

5. Run the Flask application:

   ```bash
   flask run
   ```


## API Endpoints

### Authentication

- **Login**: `POST /login`
- **Logout**: `GET /logout`

### Lesson Plan

- **Generate Lesson Plan**: `POST /generate_lesson_plan`
  - **Parameters**: `file` (PDF file), `command`, `grade`, `duration`, `subject`

### Workbook

- **Generate Workbook**: `POST /generate_workbook`
  - **Parameters**: `file` (PDF file), `command`, `grade`, `subject`

### Quiz

- **Generate Quiz**: `POST /generate_quiz` or `GET /generate_quiz`
  - **Parameters**: `topic`, `language`, `subject`, `number`, `difficulty`

### Worksheet Generation

- **Generate Worksheet**: `POST /generate`
  - **Parameters**: `subject`, `grade`, `number`, `question-type`, `sub-question-type`, `textarea`, `pdf_file`

### Gamification

- **Generate Tongue Twisters**: `POST /generate-tongue-twisters`
  - **Parameters**: `topic`, `number_of_twisters`

- **Generate Vocabulary List**: `POST /generate-vocab-list`
  - **Parameters**: `grade_level`, `subject`, `topic`, `num_words`, `difficulty_level`

- **Generate Rubric**: `POST /generate-rubric`
  - **Parameters**: `grade_level`, `assignment_description`, `point_scale`, `additional_requirements`

- **Generate Word Puzzle**: `POST /word_puzzal`
  - **Parameters**: `topic`, `numberofword`

### Summarizer

- **YouTube Summarizer**: `POST /summarize`
  - **Parameters**: `Input_URL`

## Usage

- Send requests to the API endpoints using tools like Postman or cURL.
- Ensure that all required fields are provided as per the API endpoint requirements.
- Check response status codes and messages for any errors.

## Contribution

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.
