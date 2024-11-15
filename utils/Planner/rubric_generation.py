from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def rubric_generation(grade_level, assignment_description, point_scale, additional_requirements):
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

    # Adjust the relative path to point directly to the file from the current directory
    prompt_file_path = os.path.join('prompt_template','Planner', 'Rubric_Generation.txt')
    # print(prompt_file_path)
    prompt_template = load_prompt_template(prompt_file_path)
    # print("Prompt template loaded:", prompt_template)

    if prompt_template is None:
        return "Error: Unable to load prompt template."
        
    def generate_vocab_list(grade_level, assignment_description, point_scale, additional_requirements):
    # Convert the point_scale list to a comma-separated string
        point_scale_str = ", ".join(point_scale)

        # Create the prompt using the string versions
        prompt = (
            prompt_template.replace("{grade_level}", grade_level)
            .replace("{assignment_description}", assignment_description)
            .replace("{point_scale}", point_scale_str)  # Use the converted string here
            .replace("{additional_requirements}", additional_requirements)
        )
        
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating lesson plan: {e}")
            return None

    # Logic for MCQs with a single correct answer
    output = generate_vocab_list(grade_level, assignment_description, point_scale, additional_requirements)
    
    if output is None:
        return "Error: Unable to generate lesson plan."

    # Clean up the lesson plan output
    output = output.replace("json", "")
    output = output.replace("```", "")
    print("Cleaned Output:", output)
    
    return output
