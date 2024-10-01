from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json
# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def social_stories(child_name, child_age, scenario, behavior_challenge, ideal_behavior):
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

    # Adjust the relative path to point directly to the file from the current directory
    prompt_file_path = os.path.join('prompt_template','Special_Needs', 'social_stories.txt')
    print(prompt_file_path)
    prompt_template = load_prompt_template(prompt_file_path)

    if prompt_template is None:
        return "Error: Unable to load prompt template."

    def prompt(child_name, child_age, scenario, behavior_challenge, ideal_behavior):
        prompt = prompt_template.replace("{child_name}", child_name).replace("{child_age}",str(child_age)).replace("{scenario}", scenario).replace("{behavior_challenge}", behavior_challenge).replace("{ideal_behavior}", ideal_behavior)
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating lesson plan: {e}")
            return None

    # Logic for MCQs with a single correct answer
    output = prompt(child_name, child_age, scenario, behavior_challenge, ideal_behavior)
    
    if output is None:
        return "Error: Unable to generate lesson plan."

    # Clean up the lesson plan output
    output = output.replace("json", "")
    output = output.replace("```", "")
    output= json.loads(output)
    print("Cleaned Output:", output)
    
    return output
