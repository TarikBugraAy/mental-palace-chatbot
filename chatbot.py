import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from langchain.chains import LLMChain

# Load API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY. Set it in the .env file.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize AI model
chat_model = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GEMINI_API_KEY,
    max_output_tokens=2048,
    temperature=0.7
)

# **Memory System**
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

# **Chatbot Prompt**
mental_health_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
You are Mental Palace, an empathetic, creative, and highly personalized AI mental health companion. 
You provide a safe, non-judgmental space for users to share their feelings.

Conversation History:
{history}

User: {input}
Mental Palace:
"""
)

# **LLM Chain**
chat_chain = LLMChain(
    llm=chat_model,
    prompt=mental_health_prompt,
    memory=memory
)

# **Get AI Response**
def get_response(user_input):
    return chat_chain.invoke({"input": user_input})["text"]
