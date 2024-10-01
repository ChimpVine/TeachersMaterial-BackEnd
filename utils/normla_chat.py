from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain_core.messages import AIMessage, HumanMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv
import os



# Load environment variables from .env file
load_dotenv()

# Access the environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
#yo dictionary ma sabai data user id ko adhar ma store huncha
#next phase ma eslai db ma sajilo sanga entry garna milcha
conversations = {}


def setup_conversation_chain(k=3):
    system_message = "You are a helpful assistant in maths."

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_message),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GOOGLE_API_KEY,
        stream=True,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        },
    )

    memory = ConversationBufferWindowMemory(k=k, return_messages=True)
    memory.save_context({"Human": "hi"}, {"AI": "whats up"})

    conversation = ConversationChain(
        memory=memory, prompt=prompt, llm=llm, verbose=True
    )
    
    return conversation

#user id ko adhar ma main conversation  store eta bhayeko cha
def get_conversation_chain(user_id, k=3):
    if user_id not in conversations:
        # naya user create gareko if purano chaina bhane
        conversations[user_id] = setup_conversation_chain(k)
    return conversations[user_id]


def run_math_conversation(user_id, user_input):

    conversation = get_conversation_chain(user_id)

    response = conversation.predict(input=user_input)
    print(f"Assistant (User {user_id}): {response}\n")
    return response
