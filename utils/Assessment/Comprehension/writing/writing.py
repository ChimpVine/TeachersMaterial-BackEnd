import os
import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Function to generate writing options based on difficulty
def generate_writing_options(topic, difficulty, type):
    # Initialize the LLM (model name corrected to "gpt-4")
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # Ensure you're using a valid model name
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )

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

    # Mapping difficulty levels to respective files
    type_map = {
        'essay': 'essay.txt',
        'letter': 'letter.txt'
    }
    
    # Validate the type input
    if type not in type_map:
        raise ValueError(f"Invalid type: {type}. Choose from 'essay' or 'letter'.")

    # Construct the file path for the correct prompt
    prompt_template_path = os.path.join('prompt_template', 'Assessment', 'Comprehension','writing', type_map[type])

    # Load the selected prompt template
    prompt = load_prompt_template(prompt_template_path)
    if prompt is None:
        raise Exception("Failed to load prompt template.")
    
    # Format the prompt with the provided values
    prompt = prompt.replace("{difficulty}", difficulty)
    prompt = prompt.replace("{topic}", topic)
    prompt = prompt.replace("{type}", type)
    
    # Generate the passage using the LLM
    try:
        response = llm.predict(prompt)
        cleaned_response = response.replace("\n", " ").strip()
        

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
