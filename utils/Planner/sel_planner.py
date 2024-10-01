from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Function to load prompt template
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

# Function to generate SEL plan
def sel_plan(grade, sel_topic, learning_objectives, duration):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )

    # Debugging: check current directory
    print("Current working directory:", os.getcwd())

    # Adjust the relative path to point directly to the SEL lesson plan prompt template file
    prompt_file_path = os.path.join('prompt_template','Planner', 'sel_planner.txt')
    prompt_template = load_prompt_template(prompt_file_path)
    
    if prompt_template is None:
        return None  # Handle the error as needed

    # Replace placeholders in the prompt with actual values
    prompt = prompt_template.replace("{grade}", str(grade))
    prompt = prompt.replace("{SEL topic}", sel_topic)
    prompt = prompt.replace("{learning objectives}", str(learning_objectives))
    prompt = prompt.replace("{duration}", duration)

    try:
        # Generate the lesson plan using the prompt
        response = llm.predict(prompt)
        return response
    except Exception as e:
        print(f"Error generating SEL plan: {e}")
        return None

# Main function for SEL lesson plan generation
def generate_sel():
    grade = input("Enter grade: ")
    sel_topic = input("Enter SEL topic: ")
    learning_objectives = input("Enter learning objectives (comma-separated): ").split(",")
    duration = input("Enter lesson duration (e.g., 3 hours): ")

    result = sel_plan(grade, sel_topic, learning_objectives, duration)
    
    if result is None:
        print("Failed to generate SEL lesson plan.")
        return None

    # Print the generated SEL lesson plan
    print("Generated SEL Lesson Plan:", result)
    
    return result

if __name__ == "__main__":
    generate_sel()
