from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import re, json

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def YT_summary_generation(topic):
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
    prompt_file_path=""
    prompt_file_path = os.path.join('prompt_template', 'Summarizer', 'YT-summarizer.txt')
    print(prompt_file_path)
    prompt_template = load_prompt_template(prompt_file_path)
    print("Prompt template loaded:", prompt_template)

    if prompt_template is None:
        return "Error: Unable to load prompt template."

    def generate_summary(topic):
        prompt = prompt_template.replace("{TOPIC}", topic)
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating lesson plan: {e}")
            return None

    # Logic for MCQs with a single correct answer
    output = generate_summary(topic)
    
    if output is None:
        return "Error: Unable to generate lesson plan."

    # Clean up the lesson plan output
    output = output.replace("json", "").replace("```", "")
    
    return output

def format_response_to_json(response_text):
    json_output = {}
    current_section = None
    current_text = ""

    # Regular expressions to identify headers and list items
    header_pattern = re.compile(r"\*\*(.*?)\*\*")  # Matches headers enclosed in double asterisks
    list_item_pattern = re.compile(r"^\* (.+)$", re.MULTILINE)  # Matches list items starting with a bullet point
    
    # Split response text by lines to process each line
    lines = response_text.splitlines()

    for line in lines:
        line = line.strip()  # Remove leading and trailing whitespace

        # Check if the line is a header
        header_match = header_pattern.match(line)
        if header_match:
            # Save previous section text before moving to a new section
            if current_section:
                if current_text:
                    json_output[current_section].append(current_text.strip())
                current_text = ""
            
            current_section = header_match.group(1)
            json_output[current_section] = []  # Initialize as a list for items in this section

        elif current_section:
            # Check if the line is a list item
            list_item_match = list_item_pattern.match(line)
            if list_item_match:
                # Save any accumulated text before adding list item
                if current_text:
                    json_output[current_section].append(current_text.strip())
                    current_text = ""
                
                json_output[current_section].append(list_item_match.group(1))
            else:
                # Accumulate plain text lines
                current_text += f" {line}" if current_text else line

    # Capture any remaining text after the last section
    if current_section and current_text:
        json_output[current_section].append(current_text.strip())

    # Convert dictionary to a JSON string with indentation for readability
    formatted_json = json.dumps(json_output, indent=4)
    print("this:", formatted_json)
    return formatted_json