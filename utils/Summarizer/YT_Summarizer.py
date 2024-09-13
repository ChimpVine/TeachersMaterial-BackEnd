import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from youtube_transcript_api import YouTubeTranscriptApi
import json
# Load environment variables from .env file
load_dotenv()

# Access the environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
def YT_Summarizer_generation(video_url):
    # Main function to summarize video with timestamps (local file or YouTube URL)
    def summarize_video_with_timestamps(input_source):
        if input_source.startswith(("https://")):
            try:
                video_id = extract_video_id(input_source)
                transcript_text = get_transcript(video_id)
                if transcript_text:
                    # Summarize the transcript with timestamps
                    return generate_vocab_list(transcript_text)
                else:
                    return "Error: Could not retrieve the transcript."
            except ValueError as ve:
                return str(ve)
            except Exception as e:
                print(f"Unexpected error: {e}")
                return "Error: Unable to process the input source."
        else:
            return "Error: Unsupported input source. Please provide a valid YouTube URL."
    # Function to extract video ID from a YouTube URL
    def extract_video_id(url):
        if "v=" in url:
            return url.split("v=")[-1].split("&")[0]
        raise ValueError("Invalid YouTube URL format.")

    # Function to retrieve transcript using youtube_transcript_api
    def get_transcript(video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([entry['text'] for entry in transcript])
        except Exception as e:
            print(f"Error retrieving transcript: {e}")
            return None
        
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
    prompt_file_path = os.path.join('prompt_template', 'YT_Summarizer.txt')
    print(prompt_file_path)
    prompt_template = load_prompt_template(prompt_file_path)
    print("Prompt template loaded:", prompt_template)

    if prompt_template is None:
        return "Error: Unable to load prompt template."

    def generate_vocab_list(transcript_text):
        prompt = prompt_template.replace("{transcript_text}", transcript_text)
        try:
            response = llm.predict(prompt)
            return response
        except Exception as e:
            print(f"Error generating lesson plan: {e}")
            return None
 
    # Logic for MCQs with a single correct answer
    output = summarize_video_with_timestamps(video_url)
    
    if output is None:
        return "Error: Unable to generate lesson plan."

    # Clean up the lesson plan output
    output = output.replace("json", "")
    output = output.replace("```", "")
    output=json.loads(output)
    print("Cleaned Output:", output)
    
    return output


