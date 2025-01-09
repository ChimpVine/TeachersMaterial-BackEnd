import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Function to generate data options based on difficulty
def generate_data_options(difficulty,type):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )
    
    # Debugging: check current directory
    print("Current working directory:", os.getcwd())

# Function to load the prompt template based on the difficulty
    def load_prompt_template(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    # Construct the file path for the correct prompt
    prompt_template_path = os.path.join('prompt_template', 'Assessment', 'Comprehension','writing','data_table.txt')

    # Load the selected prompt template
    prompt = load_prompt_template(prompt_template_path)
    if prompt is None:
        raise Exception("Failed to load prompt template.")
    
    # Format the prompt with the provided values
    
    
    formatted_prompt = prompt.replace("{difficulty}", difficulty).replace("{type}", (type))

    try:
        response = llm.predict(formatted_prompt)
        cleaned_response = response.replace("\n", " ").replace("\"", " ").replace("**", " ").replace("###", " ").strip()
        cleaned_response = cleaned_response.replace("  ", " ").replace("  ", " ").replace("```", " ").replace("json", " ").replace("\\n", " ").strip()
        

        try:
            parsed_output = json.loads(cleaned_response)
            return parsed_output
        except json.JSONDecodeError:
            # If not JSON, return the cleaned response directly
            return {"response": cleaned_response}
    except Exception as e:
        print(f"Error generating questions: {e}")
        return {"error": str(e)}

# Example usage:
# result = generate_writing_options("House and Home", "medium", "letter")
# print(result)
