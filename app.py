import streamlit as st
from database import init_db, create_new_session, get_sessions, rename_session, delete_session, save_chat, load_chat_history
from auth import show_auth_page
from chatbot import get_response

# Initialize database
init_db()

st.set_page_config(page_title="Mental Palace", page_icon="💬", layout="wide")

# **Display Custom Logo in Sidebar ONLY (Removed Top Logo)**
st.sidebar.image("img/logo.jpg", width=200)  # Sidebar Logo
st.title("Mental Palace - AI Mental Health Companion")

# **Login/Register System**
show_auth_page()

# **Handle Chat Sessions**
if "authenticated" in st.session_state and st.session_state["authenticated"]:
    username = st.session_state["username"]  # Store username

    # **Sidebar Section**
    st.sidebar.title(f"💬 {username}'s Chat Sessions")  # Display username

    # **Persona Selection**
    st.sidebar.markdown("### 🧠 Choose Your AI Persona")
    persona_options = {
        "Mental Palace Counselor": "The balanced and supportive AI that provides empathetic yet structured mental health support.",
        "Compassionate Listener": "A deeply empathetic AI that focuses on active listening and validation.",
        "Motivational Coach": "A high-energy AI that encourages and empowers users to take action for self-improvement.",
        "CBT Guide": "A rational AI that helps reframe negative thoughts using cognitive behavioral techniques."
    }

    selected_persona = st.sidebar.selectbox("Select a Persona:", list(persona_options.keys()), key="persona_select")
    st.session_state["selected_persona"] = selected_persona  # Store persona in session state
    st.sidebar.markdown(f"📝 *{persona_options[selected_persona]}*")

    # Fetch user chat sessions
    user_sessions = get_sessions(username)

    # **Do NOT Open a Chat Automatically** → Always start with a welcome message
    st.session_state["selected_session"] = None  # Force session to remain unselected

    # Display available chat sessions
    session_options = {session_name: session_id for session_id, session_name in user_sessions}
    selected_session_name = st.sidebar.radio("Select a chat:", list(session_options.keys()), key="session_select", index=None)

    # Update selected session when user clicks
    if selected_session_name:
        st.session_state["selected_session"] = session_options[selected_session_name]

    # **New Chat Button (User Must Manually Start)**
    if st.sidebar.button("🆕 New Chat"):
        new_session_id, new_session_name = create_new_session(username)
        if new_session_id:
            st.session_state["selected_session"] = new_session_id
            st.rerun()

    # Rename session
    new_name = st.sidebar.text_input("Rename chat:", selected_session_name if selected_session_name else "")
    if st.sidebar.button("Rename") and selected_session_name:
        rename_session(st.session_state["selected_session"], new_name)
        st.rerun()

    # Delete session
    if st.sidebar.button("🗑️ Delete Chat") and selected_session_name:
        delete_session(st.session_state["selected_session"])
        st.session_state["selected_session"] = None
        st.rerun()

    # **Display Chat Interface OR Welcome Message**
    if st.session_state["selected_session"]:
        st.write(f"💬 Chat Session: **{selected_session_name}**")
        st.write(f"🧠 AI Persona: **{st.session_state['selected_persona']}**")  # Show selected persona

        # Load chat history
        chat_history = load_chat_history(st.session_state["selected_session"])
        for message, response in chat_history:
            st.chat_message("user", avatar="🌸").write(message)  # Neutral emoji for user
            st.chat_message("assistant", avatar="🤖").write(response)  # Robot for AI

        # User input
        user_input = st.chat_input("Type your message here...")

        if user_input:
            response = get_response(username, user_input, st.session_state["selected_persona"])  # Pass persona

            # Display chat
            st.chat_message("user", avatar="🌸").write(user_input)
            st.chat_message("assistant", avatar="🤖").write(response)

            # Save conversation
            save_chat(st.session_state["selected_session"], username, user_input, response)

    else:
        # **Always Show Welcome Message on Login**
        st.markdown(f"### 👋 Welcome, {username}!")
        st.markdown("Select an existing chat from the left panel or start a **new chat** to begin.")

    # **Logout Button at Bottom of Sidebar**
    st.sidebar.markdown("---")  # Adds a separator
    if st.sidebar.button("🚪 Log Out", key="logout_button"):
        st.session_state.clear()  # Clear all session data
        st.rerun()  # Reload the app
