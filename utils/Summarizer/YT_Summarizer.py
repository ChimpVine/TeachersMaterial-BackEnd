from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json
from urllib.parse import urlparse, parse_qs

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def YT_Summarizer(video_url):
    # Initialize the OpenAI LLM client
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )

    def load_prompt_template(file_path):
        """Load the prompt template for generating the lesson plan."""
        if not os.path.isfile(file_path):
            print(f"Prompt template file not found: {file_path}")
            return ""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except (FileNotFoundError, UnicodeDecodeError) as e:
            print(f"Error loading prompt template: {str(e)}")
            return ""

    # Load the prompt template file for summarization
    prompt_file_path = os.path.join('prompt_template', 'Summarizer', 'YT_Summarizer.txt')
    prompt_template = load_prompt_template(prompt_file_path)

    if not prompt_template:
        return "Error: Unable to load prompt template."

    def prompt(summary_loaded):
        """Generate the lesson plan using the summary."""
        try:
            generated_prompt = prompt_template.replace("{summary}", str(summary_loaded))
            response = llm.predict(generated_prompt)
            return response
        except Exception as e:
            print(f"Error generating output: {e}")
            return None

    def get_video_id(url):
        """Extract the video ID from a YouTube URL."""
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            query = parse_qs(parsed_url.query)
            return query.get('v', [None])[0]
        elif parsed_url.hostname in ['youtu.be']:
            return parsed_url.path.lstrip('/')
        else:
            raise ValueError('Invalid YouTube URL')

    def fetch_transcript(video_id, language='en'):
        """Fetch the transcript of the YouTube video."""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript([language])
            return transcript.fetch()
        except TranscriptsDisabled:
            print("Transcripts are disabled for this video.")
        except NoTranscriptFound:
            print(f"No transcripts found for language '{language}'.")
        except Exception as e:
            print(f"Error fetching transcript: {e}")
        return None

    def summarize_transcript(transcript, n_sentences=5):
        """Summarize the transcript by extracting the key sentences."""
        transcript_text = [item['text'] for item in transcript]
        full_text = " ".join(transcript_text)

        # Simple summarization approach (you can use NLP libraries for better results)
        sentences = full_text.split('. ')
        summary = ". ".join(sentences[:n_sentences])  # Get the first n sentences for simplicity
        return summary

    def get_summary_with_timestamps(transcript, summary):
        """Return the summary with associated timestamps."""
        summary_with_timestamps = []
        for line in transcript:
            if line['text'] in summary:
                timestamp = line['start']
                minutes, seconds = divmod(int(timestamp), 60)
                timestamp_str = f"[{minutes}:{seconds:02d}]"
                summary_with_timestamps.append(f"{timestamp_str} {line['text']}")
        return "\n".join(summary_with_timestamps)

    # Fetch and summarize the transcript
    video_id = get_video_id(video_url)
    transcript = fetch_transcript(video_id)
    if not transcript:
        return "No transcript available."

    # Get summarized content
    summary = summarize_transcript(transcript, n_sentences=5)
    summary_with_timestamps = get_summary_with_timestamps(transcript, summary)

    # Save the summary with timestamps to a file
    def save_summary_to_file(summary_with_timestamps, file_name='summary_with_timestamps.txt'):
        """Save the summary with timestamps to a text file."""
        try:
            with open(file_name, 'w') as file:
                file.write(summary_with_timestamps)
            print(f"Summary with timestamps saved to {file_name}")
        except Exception as e:
            print(f"Error saving summary to file: {e}")

    save_summary_to_file(summary_with_timestamps)

    # Load summary from file
    def load_summary_from_file(file_name='summary_with_timestamps.txt'):
        """Load the saved summary from a text file."""
        try:
            with open(file_name, 'r') as file:
                return file.read()
        except FileNotFoundError as e:
            print(f"Error loading summary file: {str(e)}")
            return None

    summary_loaded = load_summary_from_file()

    if not summary_loaded:
        return "Error: Unable to load summary from file."
    print(summary_loaded)

    # Generate the lesson plan using the loaded summary
    output = prompt(summary_loaded)
    
    if not output:
        return "Error: Unable to generate lesson plan."

    # Clean up and process the lesson plan output
    try:
        output = output.replace("json", "").replace("```", "")
        output = json.loads(output)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from output: {str(e)}. Output was: {output}")
        return "Error: Output could not be parsed as JSON."

    # Delete the saved text file after processing
    try:
        os.remove('summary_with_timestamps.txt')
        print("Temporary file deleted successfully.")
    except OSError as e:
        print(f"Error deleting the file: {str(e)}")

    return output
