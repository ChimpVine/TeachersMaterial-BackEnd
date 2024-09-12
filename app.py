import os
import tempfile
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv


# Importing functions from utils.processor
from utils.Planner.Chat_with_lessonpanner import generate_lesson_plan
from utils.Assessment.WorkBook import generate_workbook
from utils.Assessment.quiz import quiz_generator
import os
import tempfile
import fitz  # PyMuPDF

# Importing functions from utils.worksheet module
from utils.Assessment.worksheet.mcq_single import generate_mcq_single
from utils.Assessment.worksheet.mcq_multiple import generate_mcq_multiple
from utils.Assessment.worksheet.tf_simple import generate_tf_simple
from utils.Assessment.worksheet.fib_single import generate_fib_single
from utils.Assessment.worksheet.fib_multiple import generate_fib_multiple
from utils.Assessment.worksheet.match_term_def import generate_match_term_def
from utils.Assessment.worksheet.short_answer_explain import generate_short_answer_explain
from utils.Assessment.worksheet.short_answer_list import generate_short_answer_list
from utils.Assessment.worksheet.long_answer import generate_long_answer
from utils.Assessment.worksheet.seq_events import generate_seq_events
from utils.Assessment.worksheet.ps_math import generate_ps_math

#Import Tongue Twister
from utils.Gamification.twist import Tongue_Twister
#Import Vocab list generation 
from utils.Learning.vocab import vocabulary_generation

#Import Rubric Generation 
from utils.Planner.rubric_generation import rubric_generation

#Import Cross Words
from utils.Gamification.cross_word import generate_word_search, generate_definitions

#Import Word Puzzal
#Import Word Puzzal
from utils.Gamification.Word_puzzle import Word_puzzle
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
   
    return lesson_plan

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
    
    return workbook

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
        


import fitz  # PyMuPDF
import tiktoken

def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    text = ""

    # Extract text from each page
    for page in doc:
        text += page.get_text()

    # Use tiktoken to encode the text and get the token count
    encoding = tiktoken.get_encoding("cl100k_base")  # Use the correct model encoding here
    tokens = encoding.encode(text)
    token_count = len(tokens)
    
    print("Extracted Text:", text)
    print("Token Count:", token_count)

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


# API for Tongue Twister
@app.route('/generate-tongue-twisters', methods=['POST'])
def generate_tongue_twisters():
    topic = request.form.get('topic')
    number_of_twisters = request.form.get('number_of_twisters')

    if not topic or not number_of_twisters:
        return jsonify({"error": "Please provide both 'topic' and 'number_of_twisters'"}), 400

    try:
        number_of_twisters = str(number_of_twisters)  # Ensure it's a string for prompt replacement
        result = Tongue_Twister(topic, number_of_twisters)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

# API For Vocab List Generation
@app.route('/generate-vocab-list', methods=['POST'])
def generate_vocab_list():
    grade_level = request.form.get('grade_level')
    subject = request.form.get('subject')
    topic = request.form.get('topic')
    num_words = request.form.get('num_words')
    difficulty_level = request.form.get('difficulty_level')

    # Check for required parameters
    if not all([grade_level, subject, topic, num_words, difficulty_level]):
        return jsonify({"error": "Please provide 'grade_level', 'subject', 'topic', 'num_words', and 'difficulty_level'."}), 400

    try:
        num_words = str(num_words)  # Convert num_words to string
        result = vocabulary_generation(grade_level, subject, topic, num_words, difficulty_level)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

# API For Rubric Generation
@app.route('/generate-rubric', methods=['POST'])
def generate_rubric():
    grade_level = request.form.get('grade_level')
    assignment_description = request.form.get('assignment_description')
    point_scale = request.form.getlist('point_scale')  # Assuming point_scale can be a list of strings
    additional_requirements = request.form.get('additional_requirements')

    # Check for required parameters
    if not all([grade_level, assignment_description, point_scale, additional_requirements]):
        return jsonify({"error": "Please provide 'grade_level', 'assignment_description', 'point_scale', and 'additional_requirements'."}), 400

    try:
        result = rubric_generation(grade_level, assignment_description, point_scale, additional_requirements)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500



#For Cross Word 


#For Word  Puzzal
@app.route('/word_puzzal', methods=['POST'])
def Word_puzzal():
    topic = request.form.get('topic')
    numberofword = request.form.get('numberofword')

    # Check for required parameters
    if not all([topic, numberofword]):
        return jsonify({"error": "Please provide 'topic', 'numberofword'."}), 400

    try:
        result = Word_puzzle(topic, numberofword)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)


