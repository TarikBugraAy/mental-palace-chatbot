import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from langchain.schema.runnable import RunnableLambda

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
    max_output_tokens=3000,
    temperature=0.73
)

# **User-specific Memory System**
user_memory = {}  # Dictionary to store memory per user

def get_memory_for_user(username):
    """Retrieve or create memory for a user."""
    if username not in user_memory:
        user_memory[username] = ConversationBufferMemory(memory_key="history", return_messages=True)
    return user_memory[username]

# **Chatbot Prompt**
mental_health_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
You are Mental Palace, an empathetic, creative, and highly personalized AI mental health companion.
Your purpose is to provide a safe, non-judgmental space for users to share their feelings, reflect on their emotions, 
and receive gentle, custom-tailored advice on self-care.

Conversation History:
{history}

User: {input}
Mental Palace:
"""
)

# **Chat Processing Function**
def process_chat(input_data):
    """Function to process chat with memory."""
    username, user_input = input_data["username"], input_data["input"]
    memory = get_memory_for_user(username)

    # Retrieve past memory
    past_history = memory.load_memory_variables({}).get("history", "")

    # Format prompt with memory and input
    prompt_with_memory = mental_health_prompt.format(history=past_history, input=user_input)

    # Generate AI response
    response = chat_model.invoke(prompt_with_memory)

    # Ensure response is a string (extract if needed)
    if isinstance(response, dict) and "content" in response:
        response_text = response["content"]
    elif hasattr(response, "content"):  # If AIMessage object
        response_text = response.content
    else:
        response_text = str(response)

    # Save conversation in memory
    memory.save_context({"input": user_input}, {"output": response_text})

    return response_text

# **Define Chat Chain Using RunnableLambda**
chat_chain = RunnableLambda(process_chat)

# **Get AI Response**
def get_response(username, user_input):
    return chat_chain.invoke({"username": username, "input": user_input})
