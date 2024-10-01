from langchain_openai import ChatOpenAI
from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
import requests
import json

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
app_id = os.getenv('APP_ID')


def upload_question(base64_image, user_question):
    with open("./prompt_template/image_ques.txt", "r", encoding="utf-8") as file:
        command = file.read()
    
    if user_question is not None:
        command= command.replace("{user_question}", user_question)
    else:
        command = command

    print(command)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": command},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"}},
                ]
            }
        ],
        "max_tokens": 3000
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = json.loads(response.text)

    output = response_data['choices'][0]['message']['content']
    
    output = output.replace("@", "{")
    output = output.replace("#", "}")
    output = output.replace("```json", "")
    output = output.replace("```", "")

    return output
