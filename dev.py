import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
import google.generativeai as genai

# Load API key from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Ensure API key is loaded correctly
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY. Set it in the .env file.")

# Configure Gemini API explicitly with API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize LangChain's Chat Model with Gemini
chat_model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)
memory = ConversationBufferMemory()
chat_chain = ConversationChain(llm=chat_model, memory=memory)

def chat_with_bot():
    print("💬 AI Mental Health Chatbot (Type 'exit' to stop)\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye! Take care. 💙")
            break
        response = chat_chain.predict(input=user_input)
        print(f"AI: {response}\n")

if __name__ == "__main__":
    chat_with_bot()
