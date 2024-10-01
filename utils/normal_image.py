import google.generativeai as genai
from dotenv import load_dotenv
import os
import requests
from io import BytesIO
from PIL import Image
# Load environment variables from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# Configure the Google Generative AI API
genai.configure(api_key=GOOGLE_API_KEY)

def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text

def input_image_setup(uploaded_file):
    # Read the file into bytes
    bytes_data = uploaded_file.read()
    image_parts = [
        {
            "mime_type": uploaded_file.mimetype,
            "data": bytes_data
        }
    ]
    return image_parts


def fetch_image_from_url(image_url):
    # Fetch the image from the URL
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        # Convert image to bytes
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format=image.format)
        img_byte_arr = img_byte_arr.getvalue()
        image_parts = [
            {
                "mime_type": response.headers['Content-Type'],
                "data": img_byte_arr
            }
        ]
        return image_parts
    else:
        raise Exception("Failed to retrieve image from URL")
