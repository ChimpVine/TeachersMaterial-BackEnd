from flask import Flask, render_template, request, redirect
import fitz  # PyMuPDF
import os
from langchain_openai import ChatOpenAI

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.5,
    max_tokens=4095
)

def load_prompt_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Load the prompt template
prompt_template = load_prompt_template('./prompt_template/Lesson_planner.txt')

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def generate_lesson_plan(context, command):
    prompt = prompt_template.replace("{context}", context).replace("{question}", command)
    response = llm.predict(prompt)
    return response
