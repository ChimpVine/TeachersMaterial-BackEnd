from langchain_openai import ChatOpenAI
from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
app_id = os.getenv('APP_ID')


def image_url(uri, user_question):
    with open("./prompt_template/image_url_ques.txt", "r", encoding="utf-8") as file:
        command = file.read()
        
    if user_question is not None:
        command= command.replace("{user_question}", user_question)
    else:
        command = command

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": command},
                    {"type": "image_url", "image_url": {"url": uri}},
                ],
            }
        ],
        max_tokens=3000,
    )

    output = response.choices[0].message.content
    output = output.replace("@", "{")
    output = output.replace("#", "}")
    output = output.replace("```json", "")
    output = output.replace("```", "")
    return output
