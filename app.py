import streamlit as st
from database import load_chat_history, save_chat, init_db
from auth import show_auth_page
from chatbot import get_response

# Initialize database
init_db()

# Streamlit UI
st.set_page_config(page_title="Mental Palace", page_icon="💬")

st.title("🧠 Mental Palace - AI Mental Health Companion")

# **Login/Register System**
show_auth_page()

# **Chat UI**
if "authenticated" in st.session_state and st.session_state["authenticated"]:
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
        response = get_response(user_input)

        # Display chat
        st.chat_message("user").write(user_input)
        st.chat_message("assistant").write(response)

        # Save conversation
        save_chat(st.session_state["username"], user_input, response)

    # Logout button
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.experimental_rerun()
