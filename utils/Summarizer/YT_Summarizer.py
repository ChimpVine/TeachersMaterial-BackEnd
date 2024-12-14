from youtube_transcript_api import YouTubeTranscriptApi
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json
import re

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY1')


def fetch_transcript(video_url):
    """
    Fetches the transcript and timestamps for a YouTube video.
    Accepts various formats of YouTube video URLs.
    """
    try:
        # Extract the video ID using a regular expression
        video_id_match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11})", video_url)
        if not video_id_match:
            raise ValueError("Invalid YouTube URL format.")
        
        video_id = video_id_match.group(1)
        
        # Fetch the transcript using the extracted video ID
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def format_timestamps(transcript):
    """
    Formats the timestamps from seconds to minute:second format.
    """
    for entry in transcript:
        # Convert timestamp from seconds to minute:second format
        minutes = int(entry['start'] // 60)
        seconds = int(entry['start'] % 60)
        entry['formatted_timestamp'] = f"{minutes:02d}:{seconds:02d}"
    return transcript

def load_prompt_template(file_path):
    """
    Loads the prompt template from a txt file.
    """
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

def summarize_transcript(transcript, llm, prompt_template):
    """
    Summarizes the entire transcript using the prompt template and the LLM.
    """
    formatted_transcript = "\n".join([f"Timestamp: {entry['formatted_timestamp']} | Text: {entry['text']}" for entry in transcript])
    prompt = prompt_template.replace("{transcript}", formatted_transcript)
    try:
        response = llm.predict(prompt)
        return response
    except Exception as e:
        print(f"Error summarizing transcript: {e}")
        return None

def YT_Summarizer(video_url):
    """
    Main function to fetch the transcript, process it, and generate a summary.
    """
    # Initialize the OpenAI LLM client
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095  # Limit tokens per API call
    )

    # Step 1: Fetch the transcript
    transcript = fetch_transcript(video_url)
    if not transcript:
        return "Error: Unable to fetch transcript."

    # Step 2: Format the timestamps to minute:second format
    formatted_transcript = format_timestamps(transcript)

    prompt_file_path = os.path.join('prompt_template', 'Summarizer', 'YT_Summarizer.txt')
    prompt_template = load_prompt_template(prompt_file_path)
    if not prompt_template:
        return "Error: Unable to load prompt template."

    # Step 4: Summarize the entire transcript
    summary = summarize_transcript(formatted_transcript, llm, prompt_template)
    if not summary:
        return "Error: Unable to summarize the transcript."
    
    # Clean up and process the lesson plan output
    try:
        summary = summary.replace("json", "").replace("```", "")
        summary = json.loads(summary)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from output: {str(e)}. Output was: {summary}")
        return "Error: Output could not be parsed as JSON."


    return summary