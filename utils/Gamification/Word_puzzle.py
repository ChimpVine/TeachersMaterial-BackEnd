from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import random
# Load environment variables from .env file
load_dotenv()
import json
# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# Function to create word puzzle and add missing letters based on difficulty
# Function to create word puzzle and add missing letters based on difficulty
def create_word_puzzle(data):
    puzzles = []
    
    for item in data:
        word = item['word']
        difficulty = item.get('difficulty', 'medium')  # Default to medium if no difficulty is provided
        
        # Determine how many letters to replace based on difficulty level
        if difficulty == 'easy':
            num_to_remove = len(word) // 5  # Remove ~1/5 of the letters for easy
        elif difficulty == 'medium':
            num_to_remove = len(word) // 3  # Remove ~1/3 of the letters for medium
        elif difficulty == 'hard':
            num_to_remove = len(word) // 2  # Remove ~1/2 of the letters for hard
        else:
            num_to_remove = len(word) // 3  # Default to medium behavior
        
        # Ensure at least 1 letter is removed
        num_to_remove = max(1, num_to_remove)
        
        # Randomly select letters to remove
        letters_to_remove = random.sample(word, k=num_to_remove)
        
        # Build the word puzzle by adding spaces between each character
        word_puzzle = ' '.join(['_' if char in letters_to_remove else char for char in word])
        
        # Get the list of missing letters
        missing_letters = list(set(letters_to_remove))  # Set to avoid duplicate missing letters
        
        # Add new fields to the JSON
        item['word_puzzle'] = word_puzzle
        item['missing_letters'] = missing_letters
        
        puzzles.append(item)
    
    return puzzles

    
    return puzzles
def Word_puzzle(topic, numberofword, difficulty_level):
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
    prompt_file_path = os.path.join('prompt_template','Gamification', 'word_puzzal.txt')
    print(prompt_file_path)
    prompt_template = load_prompt_template(prompt_file_path)
    print("Prompt template loaded:", prompt_template)

    if prompt_template is None:
        return "Error: Unable to load prompt template."

    def prompt(topic, numberofword, difficulty_level):
        prompt = prompt_template.replace("{topic}", topic).replace("{number_of_words}", numberofword).replace("{difficulty_level}", difficulty_level)
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating lesson plan: {e}")
            return None

    # Logic for MCQs with a single correct answer
    output = prompt(topic, numberofword, difficulty_level)
    
    if output is None:
        return "Error: Unable to generate lesson plan."

    # Clean up the lesson plan output
    output = output.replace("json", "")
    output = output.replace("```", "")
    print("Cleaned Output:", output)
    # Load the input JSON
    data = json.loads(output)

    # Create word puzzle
    puzzle_output = create_word_puzzle(data)

    # Print the new JSON output
    output_json = json.dumps(puzzle_output, indent=4)
    print(output_json)
    return output_json