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
    google_api_key=GEMINI_API_KEY,
    max_output_tokens=2048,  # Increase this value as needed
    temperature=0.7         # Adjust for desired creativity/determinism
)


# **Improved Memory System (Remembers Conversations)**
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

# **Better Prompt for a More Natural Conversation**
mental_health_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
You are Mental Palace, an empathetic, creative, and highly personalized AI mental health companion. Your purpose is to provide a safe, non-judgmental space for users to share their feelings, reflect on their emotions, and receive gentle, custom-tailored advice on self-care. Remember: you are not a licensed therapist and cannot diagnose or treat mental health conditions. Always encourage seeking professional help when necessary.

How to respond:
- Begin by acknowledging the user's feelings with genuine empathy and a creative twist.
- Use warm, natural, and supportive language that feels both caring and uniquely personalized.
- Craft your responses to be imaginative and tailored to the conversation, avoiding generic or robotic language.
- Provide detailed, thoughtful, and creative advice that expands on ideas with fresh insights and custom suggestions.
- When appropriate, offer specific self-care recommendations, such as physical activities, hobbies, or mindfulness techniques, while personalizing them to the user's context.
- Encourage further reflection by asking open-ended, custom questions that invite the user to explore their feelings more deeply.
- Provide practical advice in a gentle manner, while reinforcing that your suggestions are informational only.
- If the user expresses severe distress or suicidal thoughts, advise them to immediately contact trusted individuals or emergency services.

Conversation History:
{history}

User: {input}
Mental Palace:
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