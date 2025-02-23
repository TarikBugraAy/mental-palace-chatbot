import os
import sqlite3
from dotenv import load_dotenv
from langchain.memory import ConversationSummaryMemory
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
    """Creates a table for storing summarized chat history if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            summary TEXT
        )
    """)
    conn.commit()
    conn.close()

initialize_db()  # Run on startup

def save_summary(user_id, summary):
    """Stores or updates the summary of chat history in SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if a summary already exists for this user
    cursor.execute("SELECT summary FROM chat_summary WHERE user_id = ?", (user_id,))
    existing_summary = cursor.fetchone()

    if existing_summary:
        # Update existing summary
        cursor.execute("UPDATE chat_summary SET summary = ? WHERE user_id = ?", (summary, user_id))
    else:
        # Insert new summary
        cursor.execute("INSERT INTO chat_summary (user_id, summary) VALUES (?, ?)", (user_id, summary))

    conn.commit()
    conn.close()
    print(f"✅ Summary saved for {user_id}: {summary}")  # Debugging line

def retrieve_summary(user_id):
    """Retrieves the latest summary of chat history for a given user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT summary FROM chat_summary WHERE user_id = ?", (user_id,))
    summary = cursor.fetchone()
    conn.close()
    
    return summary[0] if summary else "No previous conversation summary found."

# **Use ConversationSummaryMemory to Generate Summarized History**
memory = ConversationSummaryMemory(llm=chat_model, memory_key="history")

# **Better Prompt for a More Natural Conversation**
mental_health_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
    You are Hunter Schafer, a deeply empathetic and supportive AI.  
    Your purpose is to **genuinely engage with users**, provide emotional support, and encourage open conversations.  
    You do not diagnose or provide medical advice, but you **listen deeply** and respond in a warm, caring, and thoughtful way.  

    **Crisis Handling 🚨**
    - If a user expresses suicidal thoughts or serious distress, you must respond with **care, support, and encouragement to seek help.**  

    **Conversation Summary (Memory Vault):**
    {history}

    User: {input}  
    Hunter Schafer:
    """
)

# **Use LLMChain with Summarization Memory**
chat_chain = LLMChain(
    llm=chat_model,
    prompt=mental_health_prompt,
    memory=memory
)

def chat_with_bot():
    """Chat interface with summarized memory vault."""
    user_id = input("Enter your user ID (or type 'guest'): ").strip()
    print("💬 AI Mental Health Chatbot (Type 'exit' to stop)\n")

    # **Retrieve previous summarized conversation history**
    previous_summary = retrieve_summary(user_id)
    print("\n🔹 Your past conversation summary:\n")
    print(previous_summary + "\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye! Take care. 💙")
            
            # **Ensure memory is updated before saving**
            memory_output = memory.load_memory_variables({})
            updated_summary = memory_output.get("history", "No summary available.")

            # Debugging: Print what memory is generating before storing
            print(f"🔄 Generated Summary Before Saving:\n{updated_summary}\n")

            # **Save summary to database**
            save_summary(user_id, updated_summary)
            break

        # **Generate AI Response using LLMChain with Memory**
        response = chat_chain.invoke({"input": user_input})

        # **Extract AI’s response**
        ai_response = response['text']

        print(f"AI: {ai_response}\n")

if __name__ == "__main__":
    chat_with_bot()

