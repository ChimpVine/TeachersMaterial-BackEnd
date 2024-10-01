from langchain_openai import ChatOpenAI
from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
app_id = os.getenv('APP_ID')