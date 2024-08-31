from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
def generate_short_answer_explain(subject, grade, number_of_questions, topic, pdf_text):
    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )
    # Debugging: check current directory
    print("Current working directory:", os.getcwd())
    
    def load_prompt_template(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            print(f"Unicode decoding error for file: {file_path}. Trying different encoding.")
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                return None
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    # Adjust the relative path to point directly to the file from the current directory
    prompt_file_path = os.path.join('prompt_template', 'worksheet', 'short_answer_explain.txt')
    prompt_template = load_prompt_template(prompt_file_path)
    print("Prompt template loaded:", prompt_template)

    if prompt_template is None:
        return None  # Handle the error as needed

    command = f"Lesson/chapter: {topic}\nGrade: {grade}\nSubject: {subject}\nNumber of questions: {number_of_questions}"

    def generate_lesson_plan(context, command):
        prompt = prompt_template.replace("{context}", context).replace("{question}", command)
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating lesson plan: {e}")
            return None

    # Logic for MCQs with a single correct answer
    output = generate_lesson_plan(pdf_text, command)
    
    if output is None:
        return None  # Handle the error as needed

    # Clean up the lesson plan output
    output = output.replace("```", "")
    output = output.replace("<html>", "")
    output = output.replace("</html>", "")
    output = output.replace("<body>", "")
    output = output.replace("</body>", "")
    output = output.replace("html", "")
    output = output.replace("<!DOCTYPE html>", "")
    output = output.replace("< lang=>", "")
    output = output.replace("json", "")
    print("Cleaned Output:", output)
    
    return output