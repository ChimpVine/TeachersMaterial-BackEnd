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


def process_math_question(user_input):
    question = user_input
    with open("./prompt_template/simple_ques.txt", "r", encoding="utf-8") as file:
        prompt_template = file.read()

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )

    prompt = PromptTemplate(
        input_variables=["question"],
        template=prompt_template,
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.invoke({'question': question})
    output = response['text']
    output = output.replace("@", "{")
    output = output.replace("#", "}")
    output = output.replace("```json", "")
    output = output.replace("```", "")

    return output


def process_audio(audio_file):
    try:
        # Save the uploaded audio file
        audio_file_path = 'temp_audio.mp3'
        audio_file.save(audio_file_path)
        client = OpenAI(api_key=OPENAI_API_KEY)
        # Open the audio file in binary mode
        with open(audio_file_path, "rb") as af:
            translation = client.audio.translations.create(
                model="whisper-1",
                file=af
            )

        question = translation.text
        answer = process_math_question(question)
        return answer
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        return f"Error processing audio: {e}"
