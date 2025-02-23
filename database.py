import sqlite3
import hashlib

# Initialize database
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      username TEXT UNIQUE, 
                      password TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                      id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      user TEXT, 
                      message TEXT, 
                      response TEXT)''')
    
    conn.commit()
    conn.close()

# Hash passwords for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register new user
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

# Authenticate user login
def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Save chat history
def save_chat(user, message, response):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user, message, response) VALUES (?, ?, ?)", (user, message, response))
    conn.commit()
    conn.close()

# Load chat history
def load_chat_history(user):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT message, response FROM chat_history WHERE user=?", (user,))
    history = cursor.fetchall()
    conn.close()
    return history
