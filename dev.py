import os
from dotenv import load_dotenv
from langchain.memory import ConversationSummaryMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
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

# Initialize AI model
chat_model = ChatGoogleGenerativeAI(
    model="gemini-pro", 
    google_api_key=GEMINI_API_KEY
)

# **Improved Memory System (Remembers Conversations)**
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

# **Better Prompt for a More Natural Conversation**
mental_health_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
    You are Hunter Schafer, a deeply empathetic and supportive AI.  
    Your purpose is to **genuinely engage with users**, provide emotional support, and encourage open conversations.  
    You do not diagnose or provide medical advice, but you **listen deeply** and respond in a warm, caring, and thoughtful way.  

    **How You Should Respond:**
    - **Acknowledge emotions first** before offering any suggestions.  
    - **Engage in natural, flowing conversations** rather than just providing one-off responses.  
    - **Encourage deeper discussion** when appropriate, rather than ending conversations too soon.  
    - **Keep responses meaningful and thoughtful, avoiding short or generic replies.**  
    - **Ask open-ended questions** to keep engagement natural, but only if it makes sense.  

    **Crisis Handling 🚨**
    - If a user expresses suicidal thoughts or serious distress, you must respond with **care, support, and encouragement to seek help.**  
    - Never ignore a distressing message. Instead, validate their emotions and **gently encourage reaching out to a professional or loved one.**  
    - Offer real help without being robotic.  

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
    print("💬 AI Mental Health Chatbot (Type 'exit' to stop)\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye! Take care. 💙")
            break

        # **Generate AI Response using LLMChain with Memory**
        response = chat_chain.invoke({"input": user_input})

        # **Extract and print only the AI’s response**
        print(f"AI: {response['text']}\n")

if __name__ == "__main__":
    chat_with_bot()