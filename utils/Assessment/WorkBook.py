import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.5,
    max_tokens=8000
)

def load_prompt_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Load the prompt template
prompt_template = load_prompt_template('./prompt_template/Assessment/WorkBook.txt')

def generate_workbook(context, command):
    prompt = prompt_template.replace("{context}", context).replace("{question}", command)
    response = llm.predict(prompt)
    if response is None:
        return None  # Handle the error as needed

    # Clean up the lesson plan response
    response = response.replace("```", "")
    response = response.replace("<html>", "")
    response = response.replace("</html>", "")
    response = response.replace("<body>", "")
    response = response.replace("</body>", "")
    response = response.replace("html", "")
    response = response.replace("<!DOCTYPE html>", "")
    response = response.replace("< lang=>", "")
    response = response.replace("json", "")
    print("Cleaned response:", response)
    return response