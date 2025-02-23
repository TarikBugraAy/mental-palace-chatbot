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
user_memory = {}  # Dictionary to store memory per user

def get_memory_for_user(username):
    """Retrieve or create memory for a user."""
    if username not in user_memory:
        user_memory[username] = ConversationBufferMemory(memory_key="history", return_messages=True)
    return user_memory[username]

# **Persona-Based Prompts**
persona_prompts = {
    "Mental Palace Counselor": "Balanced and supportive AI providing structured mental health support.",
    "Compassionate Listener": "Empathetic AI focused on active listening and emotional validation.",
    "Motivational Coach": "High-energy AI encouraging personal growth and goal-setting.",
    "CBT Guide": "Logical AI helping users reframe negative thoughts using CBT techniques."
}

# **Function to Get AI Response with Persona Selection**
def get_response(username, user_input, selected_persona="Mental Palace Counselor"):
    """
    Generates a chatbot response based on the selected AI persona.

    :param username: The user's username.
    :param user_input: The user's input message.
    :param selected_persona: The chosen AI persona.
    :return: The AI's response.
    """
    # Get user memory
    memory = get_memory_for_user(username)
    
    # Select persona prompt
    prompt_template = PromptTemplate(
        input_variables=["history", "input"],
        template=f"""
        You are {selected_persona}, an AI mental health companion. {persona_prompts[selected_persona]}

        Conversation History:
        {{history}}

        User: {{input}}
        {selected_persona}:
        """
    )

    # Create a new LLM Chain with the selected prompt
    chat_chain = LLMChain(
        llm=chat_model,
        prompt=prompt_template,
        memory=memory
    )

    return chat_chain.invoke({"input": user_input})["text"]
