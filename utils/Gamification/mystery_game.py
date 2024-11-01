from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def generate_mysterycase(topic, difficulty, no_of_clues):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )

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

    # Load prompt template file
    prompt_file_path = os.path.join('prompt_template', 'Gamification', 'mystery_game.txt')
    prompt_template = load_prompt_template(prompt_file_path)

    if prompt_template is None:
        return None  # Handle the error as needed

    # Replace placeholders in the prompt template
    prompt = prompt_template.replace("{case_study_topic}", topic)
    prompt = prompt.replace("{number_of_clues}", str(no_of_clues))
    prompt = prompt.replace("{difficulty_level}", difficulty)

    def generate_mystery_topic():
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating mystery case: {e}")
            return None

    # Logic for generating the mystery topic
    output = generate_mystery_topic()
    
    if output is None:
        return None  # Handle the error as needed

    # Clean up the output
    output = output.replace("```", "")
    output = output.replace("json", "")
    
    try:
        response_json = json.loads(output)

    
    except json.JSONDecodeError as e:
        response_json = {"error": f"Failed to parse JSON: {e}"}

    return response_json  