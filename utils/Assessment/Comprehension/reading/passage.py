import os
import json
# from langchain_openai import ChatOpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize LLM once
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.5,
    max_tokens=4095
)

# Function to generate passage options based on initial inputs
def generate_passage(topic, difficulty, no_of_words):

    # Load the prompt template
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

    # Construct the file path for the prompt template
    prompt_template_path = os.path.join('prompt_template', 'Assessment', 'Comprehension', 'reading','passage.txt')

    # Load the template
    prompt = load_prompt_template(prompt_template_path)
    if prompt is None:
        raise Exception("Failed to load prompt template.")
    
    # Format the prompt
    formatted_prompt = prompt.replace("{difficulty}", difficulty).replace("{topic}", topic).replace("{no_of_words}", str(no_of_words))

    # Generate the passage using the LLM
    try:
        response = llm.predict(formatted_prompt)

        # Clean up response if needed (minimal modifications)
        cleaned_response = response.strip()

        # Attempt to parse as JSON
        try:
            parsed_output = json.loads(cleaned_response)
            # Format the parsed output as a JSON string
            return json.dumps(parsed_output, indent=4)
        except json.JSONDecodeError:
            # If not JSON, return the cleaned response directly as a JSON string
            return json.dumps({"response": cleaned_response}, indent=4)
    except Exception as e:
        print(f"Error generating questions: {e}")
        return json.dumps({"error": str(e)}, indent=4)

# Example Usage
if __name__ == "__main__":
    result = generate_passage(topic="The Water Cycle", difficulty="easy", no_of_words=250)
    print("Final Output:\n", result)
