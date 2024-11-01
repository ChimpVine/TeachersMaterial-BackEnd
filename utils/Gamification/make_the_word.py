import random
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def load_prompt_template(file_path):
    """Load prompt template from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except (UnicodeDecodeError, FileNotFoundError) as e:
        print(f"Error loading file {file_path}: {e}")
        return None

def shuffle_letters(letters):
    """Shuffle the given letters."""
    shuffled = letters[:]
    random.shuffle(shuffled)
    return shuffled

def generate_make_the_word(theme, difficulty_level, number_of_words):
    """Generate a word-building game based on theme, difficulty level, and number of words."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )
    
    prompt_file_path = os.path.join('prompt_template', 'Gamification', 'make_the_word.txt')
    prompt_template = load_prompt_template(prompt_file_path)

    if prompt_template is None:
        return "Error: Unable to load prompt template."

    # Replace placeholders in the prompt
    prompt = prompt_template.replace("{theme}", theme) \
                            .replace("{difficulty_level}", difficulty_level) \
                            .replace("{number_of_words}", str(number_of_words))
    
    try:
        # Use the invoke method instead of predict
        response = llm.invoke(prompt)

        # Extract the text from the response
        if response is None or not hasattr(response, 'content'):
            return "Error: Received an invalid response from the model."

        response_text = response.content if hasattr(response, 'content') else str(response)

        # Debugging: print the raw response
        print("Raw response from the model:", response_text)
    except Exception as e:
        return f"Error generating word-building game: {e}"
    
    # Remove any backticks, 'json', and JSON format
    response_text = response_text.strip("` \n").replace("json", "").strip()

    if not response_text:
        return "Error: Received an empty response from the model."

    # Debugging: print the processed response
    # print("Processed response for JSON parsing:", response_text)

    try:
        # Directly parse the response into JSON
        response_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print("Raw response for debugging:", response_text)  # Debugging
        return f"Error decoding JSON response: {e}"

    # Process the generated words
    words_data = response_json.get('words', [])
    
    # Create a list of words and hints
    words_with_hints = []
    for word_info in words_data:
        word = word_info['word']
        hint = word_info['hint']
        words_with_hints.append({'word': word, 'hint': hint})  # Collect word and hint as a dict

    # Gather unique letters from all words
    unique_letters = set()
    for word in words_with_hints:
        unique_letters.update(word['word'])  # Add letters of each word

    # Add the unique letters to the response JSON
    response_json['letters'] = shuffle_letters([letter.upper() for letter in unique_letters])  # Shuffle and uppercase letters

    # Add words and hints directly to the response JSON
    response_json['words'] = words_with_hints

    # Return the final formatted output
    return json.dumps(response_json, indent=2)

# Example usage
# result = generate_word_building("astronomy", "difficult", 5)  # Here, 5 is the number of words requested
# print(result)