import os
import tempfile
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv


# Importing functions from utils.processor
from utils.Chat_with_lessonpanner import  generate_lesson_plan
from utils.WorkBook import  generate_workbook
from utils.quiz import quiz_generator
import os
import tempfile
import fitz  # PyMuPDF

# Importing functions from utils.worksheet module
from utils.worksheet.mcq_single import generate_mcq_single
from utils.worksheet.mcq_multiple import generate_mcq_multiple
from utils.worksheet.tf_simple import generate_tf_simple
from utils.worksheet.fib_single import generate_fib_single
from utils.worksheet.fib_multiple import generate_fib_multiple
from utils.worksheet.match_term_def import generate_match_term_def
from utils.worksheet.short_answer_explain import generate_short_answer_explain
from utils.worksheet.short_answer_list import generate_short_answer_list
from utils.worksheet.long_answer import generate_long_answer
from utils.worksheet.seq_events import generate_seq_events
from utils.worksheet.ps_math import generate_ps_math

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session management

# Allow requests from any origin for the specified routes
CORS(app, resources={r"/*": {"origins": "*"}})


# Get credentials from environment variables
USER_EMAIL = os.getenv('USER_EMAIL')
USER_PASSWORD = os.getenv('USER_PASSWORD')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == USER_EMAIL and password == USER_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))


import tempfile
# Ensure the temporary upload directory exists
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/generate_lesson_plan', methods=['POST'])
def api_generate_lesson_plan():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    lesson = request.form.get('command')
    grade = request.form.get('grade')
    duration = request.form.get('duration')
    subject = request.form.get('subject')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not all([lesson, grade, duration, subject]):
        return jsonify({"error": "Missing required fields"}), 400

    # Save the file temporarily
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(pdf_path)

    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    command = f"Lesson: {lesson}\nGrade: {grade}\nDuration: {duration}\nSubject: {subject}"
    lesson_plan = generate_lesson_plan(pdf_text, command)
    
    # Clean up the temporary file
    os.remove(pdf_path)
    
    lesson_plan = lesson_plan.replace("```", "").replace("html", "").replace("{", "").replace("}", "").replace("<html>", "").replace("</html>", "").replace("<body>", "").replace("</body>", "").replace("<!DOCTYPE html>", "").replace('< lang="en">', "").replace("\n", "").replace("<>", "")
    
    return jsonify({"lesson_plan": lesson_plan})

@app.route('/generate_workbook', methods=['POST'])
def api_generate_workbook():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    lesson = request.form.get('command')
    grade = request.form.get('grade')
    subject = request.form.get('subject')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not all([lesson, grade, subject]):
        return jsonify({"error": "Missing required fields"}), 400

    # Save the file temporarily
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(pdf_path)

    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    command = f"Lesson: {lesson}\nGrade: {grade}\nSubject: {subject}"
    workbook = generate_workbook(pdf_text, command)
    
    # Clean up the temporary file
    os.remove(pdf_path)
    
    workbook = workbook.replace("```", "").replace("html", "").replace("{", "").replace("}", "").replace("<html>", "").replace("</html>", "").replace("<body>", "").replace("</body>", "").replace("<!DOCTYPE html>", "").replace('< lang="en">', "").replace("\n", "").replace("<>", "")
    
    return jsonify({"workbook": workbook})

import time

@app.route('/generate_quiz', methods=['POST', 'GET'])
def generate_quiz():
    if request.method == 'POST':
        topic = request.form.get('topic') or request.json.get('topic')
        language = request.form.get('language') or request.json.get('language')
        subject = request.form.get('subject') or request.json.get('subject')
        number = request.form.get('number') or request.json.get('number')
        difficulty = request.form.get('difficulty') or request.json.get('difficulty')
        start_time = time.time()
        quiz = quiz_generator(topic, language, subject, number, difficulty)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(elapsed_time)
        return quiz
    
    elif request.method == 'GET':
        topic = request.args.get('topic')
        language = request.args.get('language')
        subject = request.args.get('subject')
        number = request.args.get('number')
        difficulty = request.args.get('difficulty')
        start_time = time.time()
        quiz = quiz_generator(topic, language, subject, number, difficulty)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(elapsed_time)
        return quiz
        


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

@app.route('/generate', methods=['POST', 'GET'])
def generate():
    subject = request.form.get('subject')
    grade = request.form.get('grade')
    number_of_questions = request.form.get('number')
    question_type = request.form.get('question-type')
    sub_question_type = request.form.get('sub-question-type')
    topic = request.form.get('textarea')
    file = request.files.get('pdf_file')
    
    pdf_text = None

    # Save the uploaded file temporarily
    if file:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        pdf_text = extract_text_from_pdf(temp_path)
        os.remove(temp_path)  # Remove the file after processing

    # Process input based on question type and sub-question type
    if question_type == "MCQ" and sub_question_type == "MCQ_Single":
        return generate_mcq_single(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "MCQ" and sub_question_type == "MCQ_Multiple":
        return generate_mcq_multiple(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "TF_Simple":
        return generate_tf_simple(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "Fill-in-the-Blanks" and sub_question_type == "FIB_Single":
        return generate_fib_single(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "Fill-in-the-Blanks" and sub_question_type == "FIB_Multiple":
        return generate_fib_multiple(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "Match_Term_Def":
        return generate_match_term_def(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "Q&A"and sub_question_type == "Short_Answer_Explain":
        return generate_short_answer_explain(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "Q&A"and sub_question_type == "Short_Answer_List":
        return generate_short_answer_list(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "Q&A"and sub_question_type == "Long_Answer_Explain":
        return generate_long_answer(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "Sequencing":
        return generate_seq_events(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "Problem_Solving":
        return generate_ps_math(subject, grade, number_of_questions, topic, pdf_text)
    else:
        return "Question type not supported."



if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0', port=5050)

