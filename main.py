import os
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from langchain.chains import LLMChain
import hashlib

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

# **Conversation Memory**
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

# **Prompt Template**
mental_health_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
You are Mental Palace, an empathetic, creative, and highly personalized AI mental health companion. 
Your purpose is to provide a safe, non-judgmental space for users to share their feelings. 
Remember: you are not a licensed therapist and cannot diagnose or treat mental health conditions. 
Always encourage seeking professional help when necessary.

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

# **Database Setup**
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      username TEXT UNIQUE, 
                      password TEXT)''')

    # Create chat history table
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                      id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      user TEXT, 
                      message TEXT, 
                      response TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# **User Authentication Functions**
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# **Save Chat History**
def save_chat(user, message, response):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user, message, response) VALUES (?, ?, ?)", (user, message, response))
    conn.commit()
    conn.close()

# **Load Chat History**
def load_chat_history(user):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT message, response FROM chat_history WHERE user=?", (user,))
    history = cursor.fetchall()
    conn.close()
    return history

# **Streamlit UI**
st.set_page_config(page_title="AI Mental Health Chatbot", page_icon="💬")

st.title("🧠 Mental Palace - AI Mental Health Companion")

# **Login/Register Panel**
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = None

if not st.session_state["authenticated"]:
    option = st.radio("Login or Register", ["Login", "Register"])

    username = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")

    if option == "Register":
        if st.button("Sign Up"):
            if register_user(username, password):
                st.success("Account created! Please log in.")
            else:
                st.error("Username already exists.")

    if option == "Login":
        if st.button("Log In"):
            if authenticate_user(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid username or password.")

else:
    st.write(f"👋 Welcome, **{st.session_state['username']}**!")
    st.write("Type below to chat with the AI.")

    # Load past chat history
    chat_history = load_chat_history(st.session_state["username"])
    
    # Display chat history
    for message, response in chat_history:
        st.chat_message("user").write(message)
        st.chat_message("assistant").write(response)

    # User input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Generate AI Response
        response = chat_chain.invoke({"input": user_input})["text"]
        
        # Display conversation
        st.chat_message("user").write(user_input)
        st.chat_message("assistant").write(response)

        # Save conversation to DB
        save_chat(st.session_state["username"], user_input, response)

    # Logout button
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.experimental_rerun()
