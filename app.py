import os
import tempfile
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import requests
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import fitz  # PyMuPDF
import json
import time
import tiktoken
# Importing functions from utils.processor
from utils.Planner.Chat_with_lessonpanner import generate_lesson_plan
from utils.Assessment.WorkBook import generate_workbook
from utils.Assessment.quiz import quiz_generator

# Importing various worksheet functions from utils.Assessment.worksheet
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

# Import Tongue Twister
from utils.Gamification.twist import Tongue_Twister

# Import Vocab list generation
from utils.Learning.vocab import vocabulary_generation

# Import Rubric Generation
from utils.Planner.rubric_generation import rubric_generation

# Import YT Summarizer
from utils.Summarizer.YT_Summarizer import YT_Summarizer

# Import Word Puzzle
from utils.Gamification.Word_puzzle import Word_puzzle

# Import Group Work
from utils.Assessment.group_work import generate_group_work

# Import Vedic Math
from utils.Learning.Vadic_math import Vadic_math

# Import Social Stories
from utils.Special_Needs.social_stories import social_stories

# For fun maths
from utils.Gamification.fun_maths import math_problem_generation

# For slide generation
from utils.Assessment import slide_one
from utils.Assessment import slide_two
# For text summarizer
from utils.Summarizer.text_summarizer import summary_generation

# For teacher joke generator
from utils.Gamification.teacher_joke import generate_joke

# For SEL planner
from utils.Planner.sel_planner import sel_generation

# For Make the Word game
from utils.Gamification.make_the_word import generate_make_the_word

# For bingo game
from utils.Gamification.bingo import generate_bingo

# For mystery case game
from utils.Gamification.mystery_game import generate_mysterycase

# For SAT math quiz
from utils.Assessment.SAT.SAT_maths import generate_math_quiz

# For Google Sheets update
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


# Ensure the temporary upload directory exists
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def extract_text_from_pdf(pdf_path):
    # Open the PDF file and extract text
    with fitz.open(pdf_path) as doc:
        text = "".join(page.get_text() for page in doc)

    # Use tiktoken to encode the text and get the token count
    encoding = tiktoken.get_encoding("cl100k_base")  # Use the correct model encoding here
    token_count = len(encoding.encode(text))
    
    print("Extracted Text:", text)
    print("Token Count:", token_count)

    return text


@app.route('/generate_lesson_plan', methods=['POST'])
def api_generate_lesson_plan():
    file = request.files.get('file')
    lesson = request.form.get('command')
    grade = request.form.get('grade')
    duration = request.form.get('duration')
    subject = request.form.get('subject')
    print(file,lesson,grade,duration, subject)

    if not all([file, lesson, grade, duration, subject]):
        return jsonify({"error": "Missing required fields or file"}), 400

    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(pdf_path)

    pdf_text = extract_text_from_pdf(pdf_path)
    command = f"Lesson: {lesson}\nGrade: {grade}\nDuration: {duration}\nSubject: {subject}"
    lesson_plan = generate_lesson_plan(pdf_text, command)

    os.remove(pdf_path)
    return lesson_plan


@app.route('/generate_workbook', methods=['POST'])
def api_generate_workbook():
    file = request.files.get('file')
    lesson = request.form.get('command')
    grade = request.form.get('grade')
    subject = request.form.get('subject')

    if not all([file, lesson, grade, subject]):
        return jsonify({"error": "Missing required fields or file"}), 400

    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(pdf_path)

    pdf_text = extract_text_from_pdf(pdf_path)
    command = f"Lesson: {lesson}\nGrade: {grade}\nSubject: {subject}"
    workbook = generate_workbook(pdf_text, command)

    os.remove(pdf_path)
    return workbook


@app.route('/generate_quiz', methods=['POST', 'GET'])
def generate_quiz():
    if request.method == 'POST':
        data = request.form or request.json
    else:
        data = request.args

    topic = data.get('topic')
    language = data.get('language')
    subject = data.get('subject')
    number = data.get('number')
    difficulty = data.get('difficulty')

    start_time = time.time()
    quiz = quiz_generator(topic, language, subject, number, difficulty)
    print("Time taken:", time.time() - start_time)
    
    return quiz


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
    elif question_type == "Q&A" and sub_question_type == "Short_Answer_Explain":
        return generate_short_answer_explain(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "Q&A" and sub_question_type == "Short_Answer_List":
        return generate_short_answer_list(subject, grade, number_of_questions, topic, pdf_text)
    elif question_type == "Q&A" and sub_question_type == "Long_Answer_Explain":
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
        result = Tongue_Twister(topic, number_of_twisters)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate-vocab-list', methods=['POST'])
def generate_vocab_list():
    data = request.form or request.json
    grade_level = data.get('grade_level')
    subject = data.get('subject')
    topic = data.get('topic')
    num_words = data.get('num_words')
    difficulty_level = data.get('difficulty_level')

    if not all([grade_level, subject, topic, num_words, difficulty_level]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        result = vocabulary_generation(grade_level, subject, topic, num_words, difficulty_level)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate-rubric', methods=['POST'])
def generate_rubric():
    data = request.form or request.json
    grade_level = data.get('grade_level')
    assignment_description = data.get('assignment_description')
    point_scale = data.getlist('point_scale')
    additional_requirements = data.get('additional_requirements')

    if not all([grade_level, assignment_description, point_scale, additional_requirements]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        result = rubric_generation(grade_level, assignment_description, point_scale, additional_requirements)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/word_puzzle', methods=['POST'])
def Word_puzzle_API():
    data = request.get_json() or request.form
    topic = data.get('topic')
    numberofword = data.get('numberofword')
    difficulty_level = data.get('difficulty_level')

    if not all([topic, numberofword, difficulty_level]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        result = Word_puzzle(topic, numberofword, difficulty_level)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/group_work', methods=['POST'])
def Group_work_API():
    data = request.form or request.json
    subject = data.get('subject')
    grade = data.get('grade')
    topic = data.get('topic')
    learning_objective = data.get('learning_objective')
    group_size = data.get('group_size')

    if not all([subject, grade, topic, learning_objective, group_size]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        result = generate_group_work(subject, grade, topic, learning_objective, group_size)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/YT_summarize', methods=['POST'])
def summarize():
    data = request.json
    video_url = data.get("video_url")
    print(video_url)

    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    try:
        result = YT_Summarizer(video_url)
        
        # Check if the result contains "No transcript available."
        if result == "No transcript available.":
            return jsonify({"error": "Subtitle not available for this video."}), 400
        
        # Check if the result contains an error message
        if isinstance(result, str) and "Error" in result:
            return jsonify({"error": result}), 500
        
        print(result)
        return result

    except Exception as e:
        # Log the exception for debugging
        print(f"Exception occurred: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}),500

@app.route("/Vadic_math", methods=['POST'])
def Vadic_math_API():
    data = request.form or request.json
    Input_URL = data.get('Input_URL')

    if not Input_URL:
        return jsonify({"error": "Please provide 'Input_URL'."}), 400

    try:
        result = Vadic_math(Input_URL)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/Social_stories", methods=['POST'])
def Social_stories_API():
    data = request.form or request.json
    child_name = data.get('child_name')
    child_age = data.get('child_age')
    scenario = data.get('scenario')
    behavior_challenge = data.get('behavior_challenge')
    ideal_behavior = data.get('ideal_behavior')

    if not all([child_name, child_age, scenario, behavior_challenge, ideal_behavior]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        result = social_stories(child_name, child_age, scenario, behavior_challenge, ideal_behavior)
        return jsonify(result)
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/fun_maths', methods=['POST'])
def generate_fun_math_API():
    data = request.form or request.json
    grade_level = data.get('grade_level')
    math_topic = data.get('math_topic')
    interest = data.get('interest')

    if not all([grade_level, math_topic, interest]):
        return jsonify({"error": "Please provide grade_level, math_topic, and interest."}), 400

    try:
        result = math_problem_generation(grade_level, math_topic, interest)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/slide_one', methods=['POST'])
def slide_one_API():
    data = request.get_json() or request.form
    grade = data.get('grade')
    topic = data.get('topic')
    learning_objectives = data.get('learning_objectives')
    number_of_slides = data.get('number_of_slides')

    if not all([grade, topic, learning_objectives, number_of_slides]):
        return jsonify({'error': 'Missing required fields'}), 400

    response = slide_one.first_slide(grade, topic, learning_objectives, number_of_slides)

    if response is None:
        return jsonify({'error': 'No valid response from first_slide'}), 500

    return response, 200


@app.route('/slide_two', methods=['POST'])
def slide_two_API():
    data = request.get_json() or request.form
    response_first_slide = data
    print(response_first_slide)

    response = slide_two.second_slide(response_first_slide)
    return response


@app.route('/text_summarizer', methods=['POST'])
def text_summarizer_API():
    data = request.get_json() or request.form
    text = data.get('text')
    summary_format = data.get('summary_format')

    if not all([text, summary_format]):
        return jsonify({'error': 'Missing required fields'}), 400

    word_count = len(text.split())
    if word_count > 1000:
        return jsonify({'error': 'Exceeded word limit. Please enter 1000 words only.'}), 400

    response = summary_generation(text, summary_format)

    if response is None:
        return jsonify({'error': 'No valid response from summary_generation'}), 500

    return response, 200


@app.route('/teacher_joke', methods=['POST'])
def teacher_joke_API():
    data = request.get_json() or request.form
    topic = data.get('topic')

    if not topic:
        return jsonify({'error': 'Missing required field: topic'}), 400

    response = generate_joke(topic)

    if response is None:
        return jsonify({'error': 'No valid response from teacher joke'}), 500

    return response, 200


@app.route('/generate_sel_plan', methods=['POST'])
def generate_sel_plan_API():
    data = request.get_json()
    grade = data.get('grade')
    sel_topic = data.get('sel_topic')
    learning_objectives = data.get('learning_objectives')
    duration = data.get('duration')

    if len(learning_objectives.split()) > 250:
        return jsonify({'error': 'Learning objectives must not exceed 250 words'}), 400

    response = sel_generation(grade, sel_topic, learning_objectives, duration)
    if response is None:
        return jsonify({'error': 'Failed to generate SEL plan'}), 500

    return response, 200

   
# API route for make the word game
@app.route('/make_the_word', methods=['POST'])
def make_the_word_API():
    if request.method == 'POST':
        # Get data from JSON body
        data = request.get_json()
        
        # Extract required fields from the request data
        theme=data.get('theme')
        difficulty_level=data.get('difficulty_level')
        number_of_words=data.get('number_of_words')

        # Validate the required fields
        if not all([theme, difficulty_level, number_of_words]):
            return jsonify({'error': 'Missing required field(s)'}), 400

        # Generate the make the word game
        response = generate_make_the_word(theme, difficulty_level, number_of_words)

        if response is None:
            return jsonify({'error': 'Failed to generate make the word game'}), 500

        # Return the generated make the word as a response
        return response, 200


# API route for make the word game
@app.route('/SAT_maths', methods=['POST'])
def SAT_maths_API():
    if request.method == 'POST':
        data = request.get_json()
        topic = data.get('topic')
        difficulty = data.get('difficulty')

        # Ensure all question counts are present and valid integers
        part1_qs = data.get('No-Calculator Multiple Choice', 0)
        part2_qs = data.get('No-Calculator Open Response', 0)
        part3_qs = data.get('Calculator Multiple Choice', 0)
        part4_qs = data.get('Calculator Open Response', 0)

        try:
            part1_qs = int(part1_qs)
            part2_qs = int(part2_qs)
            part3_qs = int(part3_qs)
            part4_qs = int(part4_qs)
        except (ValueError, TypeError):
            return jsonify({"error": "Number of questions must be integers."}), 400

        # Validate the required fields
        if not all([topic, difficulty, part1_qs, part2_qs, part3_qs, part4_qs]):
            return jsonify({'error': 'Missing required field(s)'}), 400

        # Generate SAT maths quiz
        response = generate_math_quiz(topic, part1_qs, part2_qs, part3_qs, part4_qs, difficulty)

        if response is None:
            return jsonify({'error': 'Failed to generate make the word game'}), 500

        # Return the generated SAT maths quiz as a response
        return response, 200
    
# Define a route for generating bingo
@app.route('/bingo', methods=['POST'])
def bingo_API():
     if request.method == 'POST':
        data = request.get_json()
        topic = data['topic']

        # Validate the required fields
        if not topic:
            return jsonify({'error': 'Missing required field'}), 400

        # Generate SAT maths quiz
        response = generate_bingo(topic)

        if response is None:
            return jsonify({'error': '"Failed to generate bingo'}), 500

        # Return the generated SAT maths quiz as a response
        return response, 200


# Define a route for generating bingo
@app.route('/mystery_game', methods=['POST'])
def mystery_game_API():
     if request.method == 'POST':
        data = request.get_json()
        topic = data['topic']
        difficulty = data['difficulty']
        no_of_clues= data['no_of_clues']

        # Validate the required fields
        if not all([topic, difficulty, no_of_clues]):
            return jsonify({'error': 'Missing required field(s)'}), 400

        # Generate mystery game
        response = generate_mysterycase(topic, difficulty, no_of_clues)

        if response is None:
            return jsonify({'error': '"Failed to generate mystery game'}), 500

        # Return the generated mystery game as a response
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