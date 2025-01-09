import os
import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def generate_english_quiz(selected_types):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )

    file_map = {
        "Passage Reading": 'passage_reading.txt',
        "Data Interpretation": 'data_interpretation.txt',
        "Sentence Completion": 'sentence_completion.txt',
        "Writing & Language": 'writing_language.txt'
    }

    # Initialize prompt with content from selected quiz type files
    prompt_template = ""
    for quiz_type in selected_types:
        if file_map.get(quiz_type):
            file_path = os.path.join('prompt_template','Assessment','SAT','SAT_english', file_map[quiz_type])
        else:
            return {"error": f"Invalid quiz type: {quiz_type}"}

        try:
            # Try reading with utf-8 encoding first
            with open(file_path, 'r', encoding='utf-8') as file:
                prompt_template += file.read() + "\n\n"
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        except UnicodeDecodeError:
            # If utf-8 fails, try latin-1 encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    prompt_template += file.read() + "\n\n"
            except Exception as e:
                return {"error": f"Error reading {file_path} with latin-1 encoding: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error reading {file_path}: {e}"}

    selected_types_str = ", ".join(selected_types)
    prompt = f"{prompt_template}\n\nUser selected types: {selected_types_str}"

    try:
        response = llm.predict(prompt)
        if not response:
            return {"error": "No response received from the model."}

        cleaned_response = response.replace("```", "").replace("json", "").strip()

        try:
            # Attempt to parse as JSON
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON output: {e}"}

    except Exception as e:
        return {"error": str(e)}

# def main(selected_types):
#     content = generate_english_quiz(selected_types)
#     if "error" in content:
#         return {
#             "status": "error",
#             "message": content["error"]
#         }
#     return {
#         "status": "success",
#         "content": content
#     }
