from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import SimpleSequentialChain
import wolframalpha
import cv2
import numpy as np
from PIL import Image
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from openai import OpenAI
import requests
import json
import os
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
app_id = os.getenv('APP_ID')

client = wolframalpha.Client(app_id)

def get_plot_url(equation):
    try:
        res = client.query(equation)
        for pod in res.pods:
            if 'Plot' in pod.title or 'plot' in pod.title:
                return next(subpod.img.src for subpod in pod.subpods)
    except Exception as e:
        return str(e)
    return None

def upscale_image(image):
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    upscale_factor = 2
    upscaled_image = cv2.resize(
        cv_image, (cv_image.shape[1] * upscale_factor, cv_image.shape[0] * upscale_factor), interpolation=cv2.INTER_CUBIC)
    upscaled_pil_image = Image.fromarray(
        cv2.cvtColor(upscaled_image, cv2.COLOR_BGR2RGB))
    return upscaled_pil_image







