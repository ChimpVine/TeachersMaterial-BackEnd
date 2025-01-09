import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def generate_joke(topic, number_of_jokes):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
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

    # Adjust the relative path to point directly to the joke prompt template file
    prompt_file_path = os.path.join('prompt_template', 'Gamification', 'teacher_joke.txt')

    prompt_template = load_prompt_template(prompt_file_path)
    print("Prompt template loaded:", prompt_template)

    if prompt_template is None:
        return None  # Handle the error as needed


    def generate_joke_topic(topic, number_of_jokes):
        # Ensure number_of_jokes is a string for prompt replacement
        prompt = prompt_template.replace("{topic}", topic).replace("{number_of_jokes}", str(number_of_jokes))
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating joke: {e}")
            return None

    # Logic for generating jokes
    output = generate_joke_topic(topic, number_of_jokes)
    
    if output is None:
        return None  # Handle the error as needed

    # Clean up the joke output
    output = output.replace("```", "").replace("json", "").replace("\n", "")

    # Parse the output into a JSON object if necessary
    try:
        jokes = json.loads(output)
    except json.JSONDecodeError:
        print("Failed to parse response as JSON. Returning raw output.")
        jokes = {"error": "Failed to decode response", "response": output}

    # Print the generated jokes
    print(json.dumps(jokes, indent=4))
    
    return jokes