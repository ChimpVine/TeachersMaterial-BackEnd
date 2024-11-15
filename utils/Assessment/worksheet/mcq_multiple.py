from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
def generate_mcq_multiple(subject, grade, number_of_questions, topic, pdf_text):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=8000
    )
    # Debugging: check current directory
    print("Current working directory:", os.getcwd())
    def load_prompt_template(file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None

    # Adjust the relative path to point directly to the file from the current directory
    prompt_file_path = os.path.join('prompt_template','Assessment', 'worksheet', 'mcq_multiple.txt')
    prompt_template = load_prompt_template(prompt_file_path)
    print(prompt_template)

    if prompt_template is None:
        return None  # Handle the error as needed

    command = f"Lesson/chapter: {topic}\nGrade: {grade}\nSubject: {subject}\nNumber of questions: {number_of_questions}"

    def generate_lesson_plan(context, command):
        prompt = prompt_template.replace("{context}", context).replace("{question}", command)
        response = llm.predict(prompt)
        return response

    # Logic for MCQs with a single correct answer
    Output = generate_lesson_plan(pdf_text, command)
        # Clean up the lesson plan output
    Output = Output.replace("```", "")
    Output = Output.replace("<html>", "")
    Output = Output.replace("</html>", "")
    Output = Output.replace("<body>", "")
    Output = Output.replace("</body>", "")
    Output = Output.replace("html", "")
    Output = Output.replace("<!DOCTYPE html>", "")
    Output = Output.replace("< lang=>", "")
    Output = Output.replace("json", "")
    print(Output)
    return Output
