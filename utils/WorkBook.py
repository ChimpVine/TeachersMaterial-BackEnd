import os
from langchain_openai import ChatOpenAI

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
prompt_template = load_prompt_template('./prompt_template/WorkBook.txt')

def generate_workbook(context, command):
    prompt = prompt_template.replace("{context}", context).replace("{question}", command)
    response = llm.predict(prompt)
    return response