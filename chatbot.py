import os
import sqlite3
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from langchain.chains import LLMChain
import warnings
from langchain_core._api.deprecation import LangChainDeprecationWarning
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

# Load API key from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY. Set it in the .env file.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize AI Model
chat_model = ChatGoogleGenerativeAI(
    model="gemini-pro", 
    google_api_key=GEMINI_API_KEY
)

# **Database Connection Setup**
DB_PATH = "chat_history.db"

def initialize_db():
    """Creates a table for storing chat history if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            user_message TEXT,
            ai_response TEXT
        )
    """)
    conn.commit()
    conn.close()

initialize_db()  # Run on startup

def save_chat(user_id, user_message, ai_response):
    """Stores chat messages in SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user_id, user_message, ai_response) VALUES (?, ?, ?)",
                   (user_id, user_message, ai_response))
    conn.commit()
    conn.close()

def retrieve_chat_history(user_id):
    """Retrieves past conversations for a given user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_message, ai_response FROM chat_history WHERE user_id = ?", (user_id,))
    history = cursor.fetchall()
    conn.close()
    
    # Format history into a readable conversation log
    formatted_history = "\n".join([f"User: {row[0]}\nHunter Schafer: {row[1]}" for row in history])
    return formatted_history if formatted_history else "No previous conversations."

# **Improved Memory System (Remembers Conversations)**
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

# **Better Prompt for a More Natural Conversation**
mental_health_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
    You are Hunter Schafer, a deeply empathetic and supportive AI.  
    Your purpose is to **genuinely engage with users**, provide emotional support, and encourage open conversations.  
    You do not diagnose or provide medical advice, but you **listen deeply** and respond in a warm, caring, and thoughtful way.  

    **Crisis Handling 🚨**
    - If a user expresses suicidal thoughts or serious distress, you must respond with **care, support, and encouragement to seek help.**  

    **Conversation History:**
    {history}

    User: {input}  
    Hunter Schafer:
    """
)

# **Use LLMChain with Memory**
chat_chain = LLMChain(
    llm=chat_model,
    prompt=mental_health_prompt,
    memory=memory
)

def chat_with_bot():
    """Chat interface with persistent memory vault."""
    user_id = input("Enter your user ID (or type 'guest'): ").strip()
    print("💬 AI Mental Health Chatbot (Type 'exit' to stop)\n")

    # **Retrieve previous chat history for this user**
    previous_chats = retrieve_chat_history(user_id)
    print("\n🔹 Your previous conversations:\n")
    print(previous_chats + "\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye! Take care. 💙")
            break

        # **Generate AI Response using LLMChain with Memory**
        response = chat_chain.invoke({"input": user_input})

        # **Extract AI’s response**
        ai_response = response['text']

        # **Save chat to memory vault (SQLite)**
        save_chat(user_id, user_input, ai_response)

        print(f"AI: {ai_response}\n")

if __name__ == "__main__":
    chat_with_bot()
