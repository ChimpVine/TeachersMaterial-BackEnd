import os
import random
import string
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI API key from .env
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set up OpenAI LLM using Langchain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.5,
    max_tokens=4095
)

# Function to generate an empty word search grid
def generate_empty_grid(size):
    return [[' ' for _ in range(size)] for _ in range(size)]

# Function to place words in the grid
def place_word(grid, word, direction, row, col):
    length = len(word)
    if direction == 'H':  # Horizontal
        for i in range(length):
            grid[row][col + i] = word[i]
    elif direction == 'V':  # Vertical
        for i in range(length):
            grid[row + i][col] = word[i]
    elif direction == 'D':  # Diagonal
        for i in range(length):
            grid[row + i][col + i] = word[i]

# Function to generate word search grid with words
def generate_word_search(words, grid_size=12):
    grid = generate_empty_grid(grid_size)
    directions = ['H', 'V', 'D']  # Horizontal, Vertical, Diagonal
    for word in words:
        placed = False
        while not placed:
            direction = random.choice(directions)
            row = random.randint(0, grid_size - len(word))
            col = random.randint(0, grid_size - len(word))
            if direction == 'H' and col + len(word) <= grid_size:
                place_word(grid, word, direction, row, col)
                placed = True
            elif direction == 'V' and row + len(word) <= grid_size:
                place_word(grid, word, direction, row, col)
                placed = True
            elif direction == 'D' and row + len(word) <= grid_size and col + len(word) <= grid_size:
                place_word(grid, word, direction, row, col)
                placed = True
    # Fill in empty spaces with random letters
    for i in range(grid_size):
        for j in range(grid_size):
            if grid[i][j] == ' ':
                grid[i][j] = random.choice(string.ascii_uppercase)
    return grid

# Function to generate vocabulary definitions using OpenAI
def generate_definitions(words):
    definitions = {}
    for word in words:
            # Adjust the relative path to point directly to the file from the current directory
        prompt_file_path = os.path.join('prompt_template','Gamification', 'Cross_word.txt')
        # Create a prompt to get a definition for the word
        prompt_template = prompt_file_path
        prompt = prompt_template.format(word=word)

        # Generate the definition from the LLM
        definition = llm(prompt).content
        definitions[word] = definition.strip()
    return definitions
