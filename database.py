import sqlite3
import hashlib
import datetime
import time

# Initialize database
def init_db():
    conn = sqlite3.connect("users.db", timeout=10)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      username TEXT UNIQUE, 
                      password TEXT)''')

    # Chat sessions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_sessions (
                      id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      user TEXT, 
                      session_name TEXT UNIQUE, 
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Chat messages table
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
                      id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      session_id INTEGER, 
                      user TEXT, 
                      message TEXT, 
                      response TEXT,
                      FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE)''')

    conn.commit()
    conn.close()

# Hash passwords securely
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register a new user
def register_user(username, password):
    conn = sqlite3.connect("users.db", timeout=10)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Authenticate user login
def authenticate_user(username, password):
    conn = sqlite3.connect("users.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Create a new chat session
def create_new_session(user):
    conn = sqlite3.connect("users.db", timeout=10)
    cursor = conn.cursor()

    # Ensure unique session names by adding a timestamp
    timestamp = time.strftime("%H-%M-%S")  # Adds hour-minute-second for uniqueness
    session_name = f"{datetime.datetime.now().strftime('%Y-%m-%d')}_{timestamp} Chat"

    try:
        cursor.execute("INSERT INTO chat_sessions (user, session_name) VALUES (?, ?)", (user, session_name))
        conn.commit()
        session_id = cursor.lastrowid
        return session_id, session_name
    except sqlite3.IntegrityError:
        return None, None  # If error occurs (e.g., duplicate session name)
    finally:
        conn.close()

# Get all chat sessions for a user
def get_sessions(user):
    conn = sqlite3.connect("users.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT id, session_name FROM chat_sessions WHERE user=? ORDER BY created_at DESC", (user,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions

# Rename a chat session
def rename_session(session_id, new_name):
    conn = sqlite3.connect("users.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("UPDATE chat_sessions SET session_name=? WHERE id=?", (new_name, session_id))
    conn.commit()
    conn.close()

# Delete a chat session
def delete_session(session_id):
    conn = sqlite3.connect("users.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_sessions WHERE id=?", (session_id,))
    conn.commit()
    conn.close()

# Save chat messages
def save_chat(session_id, user, message, response):
    conn = sqlite3.connect("users.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_messages (session_id, user, message, response) VALUES (?, ?, ?, ?)", 
                   (session_id, user, message, response))
    conn.commit()
    conn.close()

# Load chat messages from a session
def load_chat_history(session_id):
    conn = sqlite3.connect("users.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT message, response FROM chat_messages WHERE session_id=?", (session_id,))
    history = cursor.fetchall()
    conn.close()
    return history
