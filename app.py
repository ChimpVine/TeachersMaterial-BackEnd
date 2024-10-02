import os
import tempfile
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import requests
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from pytube import YouTube
import json
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

#Import YT Summarizer
from utils.Summarizer.YT_Summarizer import YT_Summarizer
#Import Word Puzzal
from utils.Gamification.Word_puzzle import Word_puzzle

#Import Group Word
from utils.Assessment.Group_work import Group_word

#For Vadic Math 
from utils.Learning.Vadic_math import Vadic_math

# Import Social Stories
from utils.Special_Needs.social_stories import social_stories

# For fun maths
from utils.Gamification.fun_maths import math_problem_generation

# For slide one
from utils.Assessment.slide_one import first_slide

# For slide two
from utils.Assessment.slide_two import second_slide

# For text summarizer
from utils.Summarizer.text_summarizer import summary_generation

# For teacher joke generator
from utils.Gamification.teacher_joke import generate_joke

# For SEL planner
from utils.Planner.sel_planner import sel_generation

# For word buiding game
from utils.Gamification.word_building import word_building_generation

# For Google sheet  
from utils.Request_sheet import update_google_sheet

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
    grade_level = request.form.get('grade_level')or request.json.get('grade_level')
    print(grade_level)
    subject = request.form.get('subject')or request.json.get('subject')
    print(subject)
    topic = request.form.get('topic')or request.json.get('topic')
    print(topic)
    num_words = request.form.get('num_words')or request.json.get('num_words')
    print(num_words)
    difficulty_level = request.form.get('difficulty_level')or request.json.get('difficulty_level')
    print(difficulty_level)

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


#For Word  Puzzal
@app.route('/word_puzzle', methods=['POST'])
def Word_puzzle_API():
    # Retrieve data from form or JSON request
    data = request.get_json() or request.form
    topic = data.get('topic')
    numberofword = data.get('numberofword')
    difficulty_level = data.get('difficulty_level')
    print(difficulty_level)

    # Check for required parameters
    if not all([topic, numberofword, difficulty_level]):
        return jsonify({"error": "Please provide 'topic', 'numberofword'."}), 400

    try:
        result = Word_puzzle(topic, numberofword, difficulty_level)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

#For Group Word
@app.route('/Group_work', methods=['POST'])
def Group_word_API():
    subject = request.form.get('subject')or request.json.get('subject')
    grade = request.form.get('grade')or request.json.get('grade')
    topic = request.form.get('topic')or request.json.get('topic')
    learning_objective = request.form.get('learning_objective')or request.json.get('learning_objective')
    group_size = request.form.get('group_size')or request.json.get('group_size')
    
    # Check for required parameters
    if not all([subject, grade, topic, learning_objective, group_size]):
        return jsonify({"error": "Please provide 'subject, grade, topic, learning_objective, group_size'."}), 400

    try:
        result = Group_word(subject, grade, topic, learning_objective, group_size)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/YT_summarize', methods=['POST'])
def summarize():
    data = request.json
    video_url = data.get("video_url")

    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    try:
        yt = YouTube(video_url)
        video_duration = yt.length  # Duration in seconds
        max_duration = 1800  # 30 minutes in seconds

        # Check if the video is longer than 30 minutes
        if video_duration > max_duration:
            return jsonify({"error": "Video is longer than 30 minutes"}), 400
        
        result = YT_Summarizer(video_url)
        # Check if the result contains an error message
        if isinstance(result, str) and "Error" in result:
            return jsonify({"error": result}), 500
        
        print(result)
        return result, 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API endpoint to Vadic Math
@app.route("/Vadic_math", methods=['POST'])
def Vadic_math_API():
    Input_URL = request.form.get('Input_URL') or request.json.get('Input_URL')

    # Check for required parameters
    if not all([Input_URL]):
        return jsonify({"error": "Please provide 'subject, grade, topic, learning_objective, group_size'."}), 400

    try:
        result = Vadic_math(Input_URL)
        return result  # Ensure result is returned as JSON
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


# API endpoint to Social Stories
@app.route("/Social_stories", methods=['POST'])
def Social_stories_API():
    child_name = request.form.get('child_name') or request.json.get('child_name')
    child_age = request.form.get('child_age') or request.json.get('child_age')
    scenario = request.form.get('scenario') or request.json.get('scenario')
    behavior_challenge = request.form.get('behavior_challenge') or request.json.get('behavior_challenge')
    ideal_behavior = request.form.get('ideal_behavior') or request.json.get('ideal_behavior')

    # Check for required parameters
    if not all([child_name, child_age, scenario, behavior_challenge, ideal_behavior]):
        return jsonify({"error": "Please provide 'child_name, child_age, scenario, behavior_challenge, ideal_behavior'."}), 400

    try:
        result = social_stories(child_name, child_age, scenario, behavior_challenge, ideal_behavior)
        return jsonify(result)  # Ensure result is returned as JSON
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


# API endpoint to fun math problem
@app.route('/fun_maths', methods=['POST'])
def generate_fun_math_API():
    # Data from post request
    grade_level = request.form.get('grade_level') or request.json.get('grade_level')
    math_topic = request.form.get('math_topic') or request.json.get('math_topic')
    interest = request.form.get('interest') or request.json.get('interest')

    # Validate input
    if not all([grade_level, math_topic, interest]):
        return jsonify({"error": "Please provide grade_level, math_topic, and interest."}), 400
    
    try:
        result = math_problem_generation(grade_level, math_topic, interest)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500
    
# API endpoint to slide one
@app.route('/slide_one', methods=['POST'])
def slide_one_API():
    if request.method == 'POST':
        # Check if the request contains JSON, else use form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        # Extracting required fields
        grade = data.get('grade')
        subject = data.get('subject')
        topic = data.get('topic')
        learning_objectives = data.get('learning_objectives')
        number_of_slides = data.get('number_of_slides')

        # Check if any required fields are missing
        if not all([grade, subject, topic, learning_objectives, number_of_slides]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Call first_slide function and check if response is valid
        response = first_slide(grade, subject, topic, learning_objectives, number_of_slides)

        if response is None:
            return jsonify({'error': 'No valid response from first_slide'}), 500

        # Return the valid response
        return response, 200
    
# API endpoint to slide two
@app.route('/slide_two', methods=['POST'])
def slide_two_API():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        response_first_slide = data.get('response_first_slide')
        response = second_slide(response_first_slide)      
        return response
    
# API endpoint to text summarizer
@app.route('/text_summarizer', methods=['POST'])
def text_summarizer_API():
    if request.method == 'POST':
        # Check if the request contains JSON, else use form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        # Extracting required fields
        text=data.get('text')
        summary_format=data.get('summary_format')

        # Check if any required fields are missing
        if not all([text, summary_format]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check word count limit (1000 words max)
        word_count = len(text.split())
        if word_count > 1000:
            return jsonify({'error': 'Exceeded word limit. Please enter 1000 words only.'}), 400

        # Call first_slide function and check if response is valid
        response = summary_generation(text, summary_format)

        if response is None:
            return jsonify({'error': 'No valid response from first_slide'}), 500

        # Return the valid response
        return response, 200

# API endpoint to teacher joke
@app.route('/teacher_joke', methods=['POST'])
def teacher_joke_API():
    if request.method == 'POST':
        # Check if the request contains JSON, else use form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        # Extracting required fields
        topic=data.get('topic')

        # Check if any required fields are missing
        if not topic:
            return jsonify({'error': 'Missing required field: topic'}), 400

        # Call first_slide function and check if response is valid
        response=generate_joke(topic)

        if response is None:
            return jsonify({'error': 'No valid response from teacher joke'}), 500

        # Return the valid response
        return response, 200

# API route for generating SEL plan
@app.route('/generate_sel_plan', methods=['POST'])
def generate_sel_plan_API():
    if request.method == 'POST':
        # Get data from JSON body
        data = request.get_json()

        # Extract required fields from the request data
        grade = data.get('grade')
        sel_topic = data.get('sel_topic')
        learning_objectives = data.get('learning_objectives')
        duration = data.get('duration')

        # Validate learning_objectives to ensure it does not exceed 250 words
        if len(learning_objectives.split()) > 250:
            return jsonify({'error': 'Learning objectives must not exceed 250 words'}), 400

        # Generate SEL plan
        response = sel_generation(grade, sel_topic, learning_objectives, duration)
        print(response)
        if response is None:
            return jsonify({'error': 'Failed to generate SEL plan'}), 500

        # Return the generated SEL plan as a response
        return response, 200
    
    
# API route for word building game
@app.route('/word_building_game', methods=['POST'])
def generate_word_building_game_API():
    if request.method == 'POST':
        # Get data from JSON body
        data = request.get_json()
        
        # Extract required fields from the request data
        difficulty_level=data.get('difficulty_level')
        number_of_levels=data.get('number_of_levels')

        # Validate the required fields
        if not all([difficulty_level, number_of_levels]):
            return jsonify({'error': 'Missing required field(s)'}), 400

        # Generate SEL plan
        response = word_building_generation(difficulty_level, number_of_levels)

        if response is None:
            return jsonify({'error': 'Failed to generate SEL plan'}), 500

        # Return the generated SEL plan as a response
        return response, 200


# API endpoint to receive data from form and update the Google Sheet
@app.route("/google_sheet", methods=['POST'])
def google_sheet():
    # Retrieve data from form or JSON request
    data = request.get_json() or request.form
    full_name = data.get('full_name')
    email = data.get('email')
    country = data.get('country')
    profession = data.get('profession')
    organization = data.get('organization')
    tools_categories = data.get('tools_categories')
    description = data.get('description')
    captcha_response = data.get('recaptchaToken')
    print(captcha_response)
    print(full_name, email, country, profession, organization, tools_categories, description)

    
    # Get sheet_id and recaptcha secret from environment variables
    sheet_id = os.getenv('SHEET_ID')
    recaptcha_secret = os.getenv('RECAPTCHA_SECRET_KEY2')

    print(recaptcha_secret)

    # Check for required parameters
    if not all([full_name, email, country, profession, organization, tools_categories, description, sheet_id, captcha_response]):
        return jsonify({"error": "Please provide all required fields."}), 400

    # Verify CAPTCHA with Google's reCAPTCHA API
    captcha_verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    captcha_verify_payload = {'secret': recaptcha_secret, 'response': captcha_response}
    captcha_verify_response = requests.post(captcha_verify_url, data=captcha_verify_payload)
    captcha_verify_result = captcha_verify_response.json()
    print(captcha_verify_result)

    if not captcha_verify_result.get('success'):
        return jsonify({"error": "Invalid CAPTCHA. Please try again."}), 400

    # Try to update the Google Sheet and return the result
    try:
        result = update_google_sheet(full_name, email, country, profession, organization, tools_categories, description, sheet_id)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500
    
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

