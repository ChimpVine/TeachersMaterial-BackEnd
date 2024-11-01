import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def generate_group_work(subject, grade, topic, learning_objective, group_size):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )
    
    # Function to load and read prompt template
    def load_prompt_template(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
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

    # Path to the prompt template file in the 'prompt' folder
    prompt_file_path = os.path.join('prompt_template', 'Assessment', 'group_work.txt')
    prompt_template = load_prompt_template(prompt_file_path)
    
    if prompt_template is None:
        print("Failed to load prompt template.")
        return None

    # Replace placeholders in the prompt template with user inputs using str.replace()
    prompt = (
        prompt_template
        .replace("{Subject}", subject)
        .replace("{Grade_Level}", grade)
        .replace("{Topic}", topic)
        .replace("{Learning_Objective}", learning_objective)
        .replace("{Group_Size}", str(group_size))  # Convert group_size to string for replacement
    )


    # Generate the group work division
    try:
        response = llm.invoke(prompt)  # Changed to invoke
        if response is None:
            print("No response received from LLM.")
            return None
    except Exception as e:
        print(f"Error generating group work division: {e}")
        return None

    # Access the content of the response correctly
    try:
        response_text = response.content  # Extract the text from the response
        cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
        cleaned_output = json.loads(cleaned_response)  
    except AttributeError as e:
        print(f"Error accessing response content: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    return cleaned_response

