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



# For Wordpress Site 
import http.client
import json
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

# Get the TEST_TOKEN from environment variables
TEST_TOKEN = os.getenv('TEST_TOKEN2')

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session management

# Allow requests from any origin for the specified routes
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('index.html')


# Ensure the temporary upload directory exists
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import json

# Load tools from the JSON file
def load_tools_from_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")
        return []
# Load tools from JSON file
tools = load_tools_from_json('Tools.json')
# Function to get tool by name
def get_tool_by_name(tools, tool_name):
    # Use case-insensitive search and handle different key casings
    return next((tool for tool in tools if tool.get('tool_name', '').lower() == tool_name.lower() or 
                 tool.get('Tool_name', '').lower() == tool_name.lower()), None)



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
    data = request.form or request.json
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract form data and file
    file = request.files.get('file')
    lesson = data.get('command')
    grade = data.get('grade')
    duration = data.get('duration')
    subject = data.get('subject')
    print(file, lesson, grade, duration, subject)

    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Lesson Planner")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")

    # Validate required fields and file
    if not all([file, lesson, grade, duration, subject]):
        return jsonify({"error": "Missing required fields or file"}), 400

    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url, Tool_ID, Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Save the uploaded file
            filename = secure_filename(file.filename)
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(pdf_path)

            # Extract text from the uploaded PDF
            pdf_text = extract_text_from_pdf(pdf_path)

            # Generate lesson plan
            command = f"Lesson: {lesson}\nGrade: {grade}\nDuration: {duration}\nSubject: {subject}"
            lesson_plan = generate_lesson_plan(pdf_text, command)

            # Clean up by removing the saved PDF file
            os.remove(pdf_path)

            # Prepare the response
            response = jsonify(lesson_plan)
            response.status_code = 200

            # Call use_token() only if the status code is 200
            if response.status_code == 200:
                use_token(auth_token, site_url, Tool_ID, Token)

            # Return the generated lesson plan
            return lesson_plan

        else:
            # Return the specific message from WordPress API
            return jsonify({"error": token_verification.get('message', 'Token verification failed')}), 403

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate_workbook', methods=['POST'])
def api_generate_workbook():
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract form data and file
    data = request.form or request.json
    file = request.files.get('file')
    lesson = data.get('command')
    grade = data.get('grade')
    subject = data.get('subject')
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Workbook")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")

    # Validate required fields and file
    if not all([file, lesson, grade, subject]):
        return jsonify({"error": "Missing required fields or file"}), 400

    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Save the uploaded file
            filename = secure_filename(file.filename)
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(pdf_path)

            # Extract text from the uploaded PDF
            pdf_text = extract_text_from_pdf(pdf_path)

            # Generate workbook
            command = f"Lesson: {lesson}\nGrade: {grade}\nSubject: {subject}"
            workbook = generate_workbook(pdf_text, command)

            # Clean up by removing the saved PDF file
            os.remove(pdf_path)

            # Prepare the response
            response = jsonify(workbook)
            response.status_code = 200

            # Call use_token() only if the status code is 200
            if response.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

            # Return the generated workbook as a response
            return workbook

        else:
            # Return the specific message from WordPress API
            return jsonify({"error": token_verification.get('message', 'Token verification failed')}), 403

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate_quiz', methods=['POST', 'GET'])
def generate_quiz():
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract data based on the request method
    if request.method == 'POST':
        data = request.form or request.json
    else:
        data = request.args

    topic = data.get('topic')
    language = data.get('language')
    subject = data.get('subject')
    number = data.get('number')
    difficulty = data.get('difficulty')

    # Validate required fields
    if not all([topic, language, subject, number, difficulty]):
        return jsonify({"error": "Missing required fields"}), 400
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Quiz")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Generate quiz
            start_time = time.time()
            quiz = quiz_generator(topic, language, subject, number, difficulty)
            print("Time taken:", time.time() - start_time)

            # Prepare the response
            response = jsonify(quiz)
            response.status_code = 200

            # Call use_token() only if the status code is 200
            if response.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

            # Return the generated quiz as a response
            return quiz

        else:
            # Return the specific message from WordPress API
            return jsonify({"error": token_verification.get('message', 'Token verification failed')}), 403

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


# @app.route('/generate', methods=['POST', 'GET'])
# def generate():
#     subject = request.form.get('subject')
#     grade = request.form.get('grade')
#     number_of_questions = request.form.get('number')
#     question_type = request.form.get('question-type')
#     sub_question_type = request.form.get('sub-question-type')
#     topic = request.form.get('textarea')
#     file = request.files.get('pdf_file')
    
#     pdf_text = None

#     # Save the uploaded file temporarily
#     if file:
#         temp_dir = tempfile.gettempdir()
#         temp_path = os.path.join(temp_dir, file.filename)
#         file.save(temp_path)
#         pdf_text = extract_text_from_pdf(temp_path)
#         os.remove(temp_path)  # Remove the file after processing

#     # Process input based on question type and sub-question type
#     if question_type == "MCQ" and sub_question_type == "MCQ_Single":
#         return generate_mcq_single(subject, grade, number_of_questions, topic, pdf_text)
#     elif question_type == "MCQ" and sub_question_type == "MCQ_Multiple":
#         return generate_mcq_multiple(subject, grade, number_of_questions, topic, pdf_text)
#     elif question_type == "TF_Simple":
#         return generate_tf_simple(subject, grade, number_of_questions, topic, pdf_text)
#     elif question_type == "Fill-in-the-Blanks" and sub_question_type == "FIB_Single":
#         return generate_fib_single(subject, grade, number_of_questions, topic, pdf_text)
#     elif question_type == "Fill-in-the-Blanks" and sub_question_type == "FIB_Multiple":
#         return generate_fib_multiple(subject, grade, number_of_questions, topic, pdf_text)
#     elif question_type == "Match_Term_Def":
#         return generate_match_term_def(subject, grade, number_of_questions, topic, pdf_text)
#     elif question_type == "Q&A" and sub_question_type == "Short_Answer_Explain":
#         return generate_short_answer_explain(subject, grade, number_of_questions, topic, pdf_text)
#     elif question_type == "Q&A" and sub_question_type == "Short_Answer_List":
#         return generate_short_answer_list(subject, grade, number_of_questions, topic, pdf_text)
#     elif question_type == "Q&A" and sub_question_type == "Long_Answer_Explain":
#         return generate_long_answer(subject, grade, number_of_questions, topic, pdf_text)
#     elif question_type == "Sequencing":
#         return generate_seq_events(subject, grade, number_of_questions, topic, pdf_text)
#     elif question_type == "Problem_Solving":
#         return generate_ps_math(subject, grade, number_of_questions, topic, pdf_text)
#     else:
#         return "Question type not supported."
@app.route('/generate', methods=['POST', 'GET'])
def generate():
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract form data and file (supports both form and JSON inputs)
    data = request.form or request.json
    file = request.files.get('pdf_file')

    subject = data.get('subject')
    grade = data.get('grade')
    number_of_questions = data.get('number')
    question_type = data.get('question-type')
    sub_question_type = data.get('sub-question-type')
    topic = data.get('textarea')
    
    # Validate required fields
    if not all([subject, grade, number_of_questions, question_type]):
        return jsonify({"error": "Missing required fields"}), 400

    pdf_text = None
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Worksheet")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    # Save the uploaded file temporarily (if provided)
    if file:
        try:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, file.filename)
            file.save(temp_path)
            pdf_text = extract_text_from_pdf(temp_path)
            os.remove(temp_path)  # Remove the file after processing
        except Exception as e:
            print(f"Error processing file: {e}")
            return jsonify({"error": "Failed to process the uploaded file"}), 500

    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Process input based on question type and sub-question type
            if question_type == "MCQ" and sub_question_type == "MCQ_Single":
                response = generate_mcq_single(subject, grade, number_of_questions, topic, pdf_text)
            elif question_type == "MCQ" and sub_question_type == "MCQ_Multiple":
                response = generate_mcq_multiple(subject, grade, number_of_questions, topic, pdf_text)
            elif question_type == "TF_Simple":
                response = generate_tf_simple(subject, grade, number_of_questions, topic, pdf_text)
            elif question_type == "Fill-in-the-Blanks" and sub_question_type == "FIB_Single":
                response = generate_fib_single(subject, grade, number_of_questions, topic, pdf_text)
            elif question_type == "Fill-in-the-Blanks" and sub_question_type == "FIB_Multiple":
                response = generate_fib_multiple(subject, grade, number_of_questions, topic, pdf_text)
            elif question_type == "Match_Term_Def":
                response = generate_match_term_def(subject, grade, number_of_questions, topic, pdf_text)
            elif question_type == "Q&A" and sub_question_type == "Short_Answer_Explain":
                response = generate_short_answer_explain(subject, grade, number_of_questions, topic, pdf_text)
            elif question_type == "Q&A" and sub_question_type == "Short_Answer_List":
                response = generate_short_answer_list(subject, grade, number_of_questions, topic, pdf_text)
            elif question_type == "Q&A" and sub_question_type == "Long_Answer_Explain":
                response = generate_long_answer(subject, grade, number_of_questions, topic, pdf_text)
            elif question_type == "Sequencing":
                response = generate_seq_events(subject, grade, number_of_questions, topic, pdf_text)
            elif question_type == "Problem_Solving":
                response = generate_ps_math(subject, grade, number_of_questions, topic, pdf_text)
            else:
                return jsonify({"error": "Question type not supported"}), 400

             # Prepare the response
            result = jsonify(response)
            result.status_code = 200
            # Call use_token() only if the status code is 200
            if result.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

            # Return the generated response
            return response, 200

        else:
            # Return the specific message from WordPress API if token verification fails
            return jsonify({"error": token_verification.get('message', 'Token verification failed')}), 403

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate-tongue-twisters', methods=['POST'])
def generate_tongue_twisters():
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract form data
    # Extract form data and file (supports both form and JSON inputs)
    data = request.form or request.json
    topic = data.get('topic')
    number_of_twisters = data.get('number_of_twisters')

    # Validate required fields
    if not topic or not number_of_twisters:
        return jsonify({"error": "Please provide both 'topic' and 'number_of_twisters'"}), 400
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Tongue Twister")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Generate tongue twisters
            result = Tongue_Twister(topic, number_of_twisters)

            # Prepare the response
            response = jsonify(result)
            response.status_code = 200

            # Call use_token() only if the status code is 200
            if response.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

            # Return the result
            return result

        else:
            # Return the specific message from WordPress API
            return jsonify({"error": token_verification.get('message', 'Token verification failed')}), 403

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate-rubric', methods=['POST'])
def generate_rubric():
    # First check if the data is coming from a form or JSON
    if request.is_json:
        data = request.get_json()  # If the content is JSON, parse it
    else:
        data = request.form  # Otherwise, handle as form data

    # Access form or JSON fields
    grade_level = data.get('grade_level')
    assignment_description = data.get('assignment_description')
    # Use getlist() if it's form data; otherwise, access directly for JSON
    if isinstance(data, dict):  # If it's a dictionary (JSON)
        point_scale = data.get('point_scale')  # Get point_scale from JSON
    else:  # If it's form data (MultiDict)
        point_scale = data.getlist('point_scale')

    additional_requirements = data.get('additional_requirements')

    # Check if all required fields are present
    if not all([grade_level, assignment_description, point_scale, additional_requirements]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Call your rubric generation function
        result = rubric_generation(grade_level, assignment_description, point_scale, additional_requirements)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/word_puzzle', methods=['POST'])
def Word_puzzle_API():
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract data from request body
    data = request.get_json() or request.form
    topic = data.get('topic')
    numberofword = data.get('numberofword')
    difficulty_level = data.get('difficulty_level')
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Word Puzzle")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    # Validate required fields
    if not all([topic, numberofword, difficulty_level]):
        return jsonify({"error": "Missing required fields"}), 400

    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Generate word puzzle
            result = Word_puzzle(topic, numberofword, difficulty_level)

            # Prepare the response
            response = jsonify(result)
            response.status_code = 200

            # Call use_token() only if the status code is 200
            if response.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

            # Return the result
            return result

        else:
            # Return the specific message from WordPress API
            return jsonify({"error": token_verification.get('message', 'Token verification failed')}), 403

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/group_work', methods=['POST'])
def Group_work_API():
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract data from request body
    data = request.form or request.json
    subject = data.get('subject')
    grade = data.get('grade')
    topic = data.get('topic')
    learning_objective = data.get('learning_objective')
    group_size = data.get('group_size')

    # Validate required fields
    if not all([subject, grade, topic, learning_objective, group_size]):
        return jsonify({"error": "Missing required fields"}), 400
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Group Work")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Generate group work activity
            result = generate_group_work(subject, grade, topic, learning_objective, group_size)

            # Prepare the response
            response = jsonify(result)
            response.status_code = 200

            # Call use_token() only if the status code is 200
            if response.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

            # Return the result
            return result

        else:
            # Return the specific message from WordPress API
            return jsonify({"error": token_verification.get('message', 'Token verification failed')}), 403

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

# @app.route('/YT_summarize', methods=['POST'])
# def summarize():
#     data = request.json
#     video_url = data.get("video_url")
#     print(video_url)

#     if not video_url:
#         return jsonify({"error": "No video URL provided"}), 400

#     try:
#         result = YT_Summarizer(video_url)
        
#         # Check if the result contains "No transcript available."
#         if result == "No transcript available.":
#             return jsonify({"error": "Subtitle not available for this video."}), 400
        
#         # Check if the result contains an error message
#         if isinstance(result, str) and "Error" in result:
#             return jsonify({"error": result}), 500
        
#         print(result)
#         return result

#     except Exception as e:
#         # Log the exception for debugging
#         print(f"Exception occurred: {e}")
#         return jsonify({"error": f"An error occurred: {str(e)}"}),500



@app.route('/YT_summarize', methods=['POST'])
def summarize():
    data = request.json
    
    # Extract headers for token verification
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(f"Video URL: {data.get('video_url')}, Site URL: {site_url}, Auth Token: {auth_token}")

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract video URL from request data
    video_url = data.get("video_url")
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "YT Summarizer")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    # Verify the token before processing the request
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)
        if token_verification.get('status') != 'success':
            return jsonify({"error": token_verification.get('message', 'Token verification failed')}), 403

        # Generate the summary if the token is valid
        result = YT_Summarizer(video_url)

        # Handle different response scenarios
        if result == "No transcript available.":
            return jsonify({"error": "Subtitle not available for this video."}), 400
        
        if isinstance(result, str) and "Error" in result:
            return jsonify({"error": result}), 500

        # If the result is valid, send the response
        response = jsonify(result)
        response.status_code = 200

        # Call use_token() only if the status code is 200
        if response.status_code == 200:
            use_token(auth_token, site_url,Tool_ID,Token)

        return result

    except Exception as e:
        # Log the exception for debugging
        print(f"Exception occurred: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

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
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract data from request body
    data = request.form or request.json
    child_name = data.get('child_name')
    child_age = data.get('child_age')
    scenario = data.get('scenario')
    behavior_challenge = data.get('behavior_challenge')
    ideal_behavior = data.get('ideal_behavior')

    # Validate required fields
    if not all([child_name, child_age, scenario, behavior_challenge, ideal_behavior]):
        return jsonify({"error": "Missing required fields"}), 400
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Social Story")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Generate social story
            result = social_stories(child_name, child_age, scenario, behavior_challenge, ideal_behavior)

            # Prepare the response
            response = jsonify(result)
            response.status_code = 200

            # Call use_token() only if the status code is 200
            if response.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

            # Return the result
            return result

        else:
            # Return the specific message from WordPress API
            return jsonify({"error": token_verification.get('message', 'Token verification failed')}), 403

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


# @app.route('/slide_one', methods=['POST'])
# def slide_one_API():
#     data = request.get_json() or request.form
#     grade = data.get('grade')
#     topic = data.get('topic')
#     learning_objectives = data.get('learning_objectives')
#     number_of_slides = data.get('number_of_slides')

#     if not all([grade, topic, learning_objectives, number_of_slides]):
#         return jsonify({'error': 'Missing required fields'}), 400

#     response = slide_one.first_slide(grade, topic, learning_objectives, number_of_slides)

#     if response is None:
#         return jsonify({'error': 'No valid response from first_slide'}), 500

#     return response, 200

@app.route('/slide_one', methods=['POST'])
def slide_one_API():
    data = request.get_json() or request.form

    # Extract headers for token verification
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(f"Grade: {data.get('grade')}, Topic: {data.get('topic')}, Site URL: {site_url}, Auth Token: {auth_token}")

    # Validate the presence of required headers
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract data from request
    grade = data.get('grade')
    topic = data.get('topic')
    learning_objectives = data.get('learning_objectives')
    number_of_slides = data.get('number_of_slides')

    # Validate required fields
    if not all([grade, topic, learning_objectives, number_of_slides]):
        return jsonify({'error': 'Missing required fields'}), 400
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Slide Generator")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    try:
        # Verify token before generating slides
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)
        if token_verification.get('status') != 'success':
            return jsonify({"error": token_verification.get('message', 'Token verification failed')}), 403

        # Generate slides using the slide_one function
        response = slide_one.first_slide(grade, topic, learning_objectives, number_of_slides)

        # Check if the response is valid
        if response is None:
            return jsonify({'error': 'No valid response from first_slide'}), 500

        # Prepare the successful response
        result = jsonify(response)
        result.status_code = 200

        # Call use_token() only if the status code is 200
        if result.status_code == 200:
            use_token(auth_token, site_url,Tool_ID,Token)

        return response

    except Exception as e:
        # Log the exception for debugging
        print(f"Exception occurred: {e}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/slide_two', methods=['POST'])
def slide_two_API():
    data = request.get_json() or request.form
    response_first_slide = data
    print(response_first_slide)

    response = slide_two.second_slide(response_first_slide)
    return response



@app.route('/text_summarizer', methods=['POST'])
def text_summarizer_API():
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({'error': "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({'error': "Missing 'X-Site-Url' header"}), 400

    # Extract data from request
    data = request.get_json() or request.form
    text = data.get('text')
    summary_format = data.get('summary_format')

    # Validate required fields
    if not all([text, summary_format]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check word count limit
    word_count = len(text.split())
    if word_count > 1000:
        return jsonify({'error': 'Exceeded word limit. Please enter 1000 words only.'}), 400
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Text Summarizer")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Generate summary
            response = summary_generation(text, summary_format)

            if response is None:
                return jsonify({'error': 'No valid response from summary_generation'}), 500

            # Prepare and return the summary response
            result = jsonify(response)
            result.status_code = 200

            # Call use_token() only if the status code is 200
            if result.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

            return response
        else:
            return jsonify({'error': token_verification.get('message', 'Token verification failed')}), 403

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500


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
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({'error': "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({'error': "Missing 'X-Site-Url' header"}), 400

    # Extract data from request
    data = request.get_json()
    grade = data.get('grade')
    sel_topic = data.get('sel_topic')
    learning_objectives = data.get('learning_objectives')
    duration = data.get('duration')
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "SEL Generator")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    # Validate the length of learning objectives
    if len(learning_objectives.split()) > 250:
        return jsonify({'error': 'Learning objectives must not exceed 250 words'}), 400

    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Generate SEL plan
            response = sel_generation(grade, sel_topic, learning_objectives, duration)

            if response is None:
                return jsonify({'error': 'Failed to generate SEL plan'}), 500

            # Prepare and return the response
            result = jsonify(response)
            result.status_code = 200

            # Call use_token() only if the status code is 200
            if result.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

            return response
        else:
            return jsonify({'error': token_verification.get('message', 'Token verification failed')}), 403

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500

# API route for make the word game
@app.route('/make_the_word', methods=['POST'])
def make_the_word_API():
    if request.method == 'POST':
        # Extract headers
        auth_token = request.headers.get('Authorization')
        site_url = request.headers.get('X-Site-Url')
        print(site_url, auth_token)

        # Check if the required headers are present
        if not auth_token:
            return jsonify({'error': "Missing 'Authorization' header"}), 400
        if not site_url:
            return jsonify({'error': "Missing 'X-Site-Url' header"}), 400

        # Get data from JSON body
        data = request.get_json()
        
        # Extract required fields from the request data
        theme = data.get('theme')
        difficulty_level = data.get('difficulty_level')
        number_of_words = data.get('number_of_words')

        # Validate the required fields
        if not all([theme, difficulty_level, number_of_words]):
            return jsonify({'error': 'Missing required field(s)'}), 400
        # Get the "Lesson Planner" tool details
        tool = get_tool_by_name(tools, "Make the Word")
        if not tool:
            return jsonify({"error": "Tool not found"}), 500

        Tool_ID = tool.get('Tool_ID')
        Token = tool.get('Token')
        print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
        # Verify tokens before proceeding
        try:
            token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

            # Check if the token verification was successful
            if token_verification.get('status') == 'success':
                # Generate the make the word game
                response = generate_make_the_word(theme, difficulty_level, number_of_words)

                if response is None:
                    return jsonify({'error': 'Failed to generate make the word game'}), 500

                # Prepare and return the response
                result = jsonify(response)
                result.status_code = 200

                # Call use_token() only if the status code is 200
                if result.status_code == 200:
                    use_token(auth_token, site_url,Tool_ID,Token)

                return response
            else:
                return jsonify({'error': token_verification.get('message', 'Token verification failed')}), 403

        except Exception as e:
            print(f"Error processing request: {e}")
            return jsonify({'error': str(e)}), 500


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


# Define a route for mystery_game
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


# # API endpoint to receive data from form and update the Google Sheet
# @app.route("/google_sheet", methods=['POST'])
# def google_sheet():
#     # Retrieve data from form or JSON request
#     data = request.get_json() or request.form
#     full_name = data.get('full_name')
#     email = data.get('email')
#     country = data.get('country')
#     profession = data.get('profession')
#     organization = data.get('organization')
#     tools_categories = data.get('tools_categories')
#     description = data.get('description')
#     captcha_response = data.get('recaptchaToken')
#     print(captcha_response)
#     print(full_name, email, country, profession, organization, tools_categories, description)

    
#     # Get sheet_id and recaptcha secret from environment variables
#     sheet_id = os.getenv('SHEET_ID')
#     recaptcha_secret = os.getenv('RECAPTCHA_SECRET_KEY2')

#     print(recaptcha_secret)

#     # Check for required parameters
#     if not all([full_name, email, country, profession, organization, tools_categories, description, sheet_id, captcha_response]):
#         return jsonify({"error": "Please provide all required fields."}), 400

#     # Verify CAPTCHA with Google's reCAPTCHA API
#     captcha_verify_url = 'https://www.google.com/recaptcha/api/siteverify'
#     captcha_verify_payload = {'secret': recaptcha_secret, 'response': captcha_response}
#     captcha_verify_response = requests.post(captcha_verify_url, data=captcha_verify_payload)
#     captcha_verify_result = captcha_verify_response.json()
#     print(captcha_verify_result)

#     if not captcha_verify_result.get('success'):
#         return jsonify({"error": "Invalid CAPTCHA. Please try again."}), 400

#     # Try to update the Google Sheet and return the result
#     try:
#         result = update_google_sheet(full_name, email, country, profession, organization, tools_categories, description, sheet_id)
#         return result
#     except Exception as e:
#         print(f"Error processing request: {e}")
#         return jsonify({"error": str(e)}), 500

# API endpoint to receive data from form and update the Google Sheet
@app.route("/google_sheet", methods=['POST'])
def google_sheet():
    # Retrieve data from form or JSON request
    data = request.get_json() or request.form
    full_name = data.get('full_name')
    email = data.get('email')
    description = data.get('description')
    captcha_response = data.get('recaptchaToken')
    print(captcha_response)
    print(full_name, email,  description)

    
    # Get sheet_id and recaptcha secret from environment variables
    sheet_id = os.getenv('SHEET_ID')
    recaptcha_secret = os.getenv('RECAPTCHA_SECRET_KEY2')

    print(recaptcha_secret)

    # Check for required parameters
    if not all([full_name, email, description, sheet_id, captcha_response]):
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
        result = update_google_sheet(full_name, email, description, sheet_id)
        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/generate-vocab-list', methods=['POST'])
def generate_vocab_list():
    data = request.form or request.json

    # Extracting headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)
    
    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extracting data from the request
    grade_level = data.get('grade_level')
    subject = data.get('subject')
    topic = data.get('topic')
    num_words = data.get('num_words')
    difficulty_level = data.get('difficulty_level')

    # Validating required fields
    if not all([grade_level, subject, topic, num_words, difficulty_level]):
        return jsonify({"error": "Missing required fields"}), 400
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Vocab List Generator")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)
        
        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # If the token is valid, generate vocabulary list
            result = vocabulary_generation(grade_level, subject, topic, num_words, difficulty_level)
             # After generating the vocabulary list, return the result
            response = jsonify(result)
            response.status_code = 200 
            # Call use_token() after sending a successful response
            use_token(auth_token, site_url,Tool_ID,Token)
            return result
        else:
            # Return the specific message from WordPress API
            return jsonify({"error": token_verification.get('message', 'Token verification failed')}), 403

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500
    

def api_request(auth_token, site_url, endpoint_suffix, Tool_ID,Token):
    """
    Helper function to perform API requests to the WordPress site.
    """
    # Parse the site URL
    parsed_url = urlparse(site_url if site_url.startswith("http") else f"https://{site_url}")
    domain, path = parsed_url.netloc, parsed_url.path.rstrip('/')

    if not auth_token or not domain:
        return {"status": "error", "message": "Authorization token and site URL are required"}
    
    # Set headers and payload
    headers = {
        'Authorization': f"Bearer {auth_token}",
        'Content-Type': 'application/json'
    }
    aitoolID = "1"
    payload = json.dumps({
        "AIToolID": Tool_ID,
        'TokenUsed': Token
    })

    try:
        # Create HTTPS connection and send request
        conn = http.client.HTTPSConnection(domain)
        endpoint = f"{path}/wp-json/teacher-tools/v1/{endpoint_suffix}"
        conn.request("POST", endpoint, payload, headers)
        
        response = conn.getresponse()
        response_data = response.read().decode()
        response_json = json.loads(response_data)
        print(f"Response Status: {response.status}")
        print(f"Response Data: {response_data}")
        # Handle response based on status code
        if response.status == 200 and response_json.get("success"):
            return {"status": "success", "message": response_json.get("message")}
        elif response.status in [400, 401, 403]:
            error_messages = {
                400: "Bad Request - Check input parameters",
                401: "Unauthorized - Invalid token",
                403: "Forbidden - Check token permissions or IP restrictions"
            }
            return {"status": "error", "message": error_messages[response.status]}
        else:
            return {"status": "error", "message": f"Unexpected status code: {response.status}"}
    except Exception as e:
        print(f"Error calling WordPress API: {e}")
        return {"status": "error", "message": "Failed to connect to WordPress API"}

def verify_token(auth_token, site_url,Tool_ID,Token):
    """
    Function to verify the token using the WordPress API.
    """
    return api_request(auth_token, site_url, "check-token",Tool_ID,Token)

def use_token(auth_token, site_url,Tool_ID,Token):
    """
    Function to use (subtract) the token using the WordPress API.
    """
    if not Token:
        print("Error: TEST_TOKEN is not set in environment variables.")
        return {"status": "error", "message": "Missing TEST_TOKEN"}
    
    return api_request(auth_token, site_url, "use-token",Tool_ID,Token)

if __name__ == '__main__':
    app.run(debug=True)
