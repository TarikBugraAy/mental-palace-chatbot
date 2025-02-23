import streamlit as st
from database import authenticate_user, register_user

def show_auth_page():
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
                    st.rerun()  
                else:
                    st.error("Invalid username or password.")
