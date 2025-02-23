import streamlit as st
from database import init_db, create_new_session, get_sessions, rename_session, delete_session, save_chat, load_chat_history
from auth import show_auth_page
from chatbot import get_response

# Initialize database
init_db()

st.set_page_config(page_title="Mental Palace", page_icon="💬", layout="wide")

# **Display Custom Logo**
st.image("img/logo.jpg", width=120)  # Main Page Logo
st.title("Mental Palace - AI Mental Health Companion")

# **Login/Register System**
show_auth_page()

# **Handle Chat Sessions**
if "authenticated" in st.session_state and st.session_state["authenticated"]:
    username = st.session_state["username"]  # Store username

    # **Sidebar Section**
    st.sidebar.image("img/logo.jpg", width=200)  # Sidebar Logo
    st.sidebar.title(f"💬 {username}'s Chat Sessions")  # Display username

    # Fetch user chat sessions
    user_sessions = get_sessions(username)

    # Ensure a default chat session is created on login
    if not user_sessions:
        new_session_id, new_session_name = create_new_session(username)
        user_sessions = [(new_session_id, new_session_name)]  # Add new session to list

    # Store session selection
    if "selected_session" not in st.session_state:
        st.session_state["selected_session"] = user_sessions[0][0]  # Default to first session

    # Display available chat sessions
    session_options = {session_name: session_id for session_id, session_name in user_sessions}
    selected_session_name = st.sidebar.radio("Select a chat:", list(session_options.keys()), key="session_select")

    # Update selected session
    if selected_session_name:
        st.session_state["selected_session"] = session_options[selected_session_name]

    # New chat button
    if st.sidebar.button("🆕 New Chat"):
        new_session_id, new_session_name = create_new_session(username)
        if new_session_id:
            st.session_state["selected_session"] = new_session_id
            st.rerun()

    # Rename session
    new_name = st.sidebar.text_input("Rename chat:", selected_session_name)
    if st.sidebar.button("Rename"):
        rename_session(st.session_state["selected_session"], new_name)
        st.rerun()

    # Delete session
    if st.sidebar.button("🗑️ Delete Chat"):
        delete_session(st.session_state["selected_session"])
        st.session_state["selected_session"] = None
        st.rerun()

    # **Chat Interface**
    if st.session_state["selected_session"]:
        st.write(f"💬 Chat Session: **{selected_session_name}**")

        # Load chat history
        chat_history = load_chat_history(st.session_state["selected_session"])
        for message, response in chat_history:
            st.chat_message("user").write(message)
            st.chat_message("assistant").write(response)

        # User input
        user_input = st.chat_input("Type your message here...")

        if user_input:
            response = get_response(st.session_state["username"], user_input)  # Ensures correct user memory

            # Display chat
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write(response)

            # Save conversation
            save_chat(st.session_state["selected_session"], username, user_input, response)

    # **Logout Button at Bottom of Sidebar**
    st.sidebar.markdown("---")  # Adds a separator
    if st.sidebar.button("🚪 Log Out", key="logout_button"):
        st.session_state.clear()  # Clear all session data
        st.rerun()  # Reload the app
