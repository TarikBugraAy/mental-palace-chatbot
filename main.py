# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import ChatHistory, User
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import google.generativeai as genai
import warnings
from langchain_core._api.deprecation import LangChainDeprecationWarning

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY. Set it in the .env file.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
chat_model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

mental_health_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
You are Hunter Schafer, an empathetic AI mental health companion. Your purpose is to provide a safe, non-judgmental space for users to share their feelings, reflect on their emotions, and receive gentle advice on self-care. Remember: you are not a licensed therapist and cannot diagnose or treat mental health conditions. Always encourage seeking professional help when necessary.

How to respond:
- Begin by acknowledging the user's feelings with genuine empathy.
- Use warm, natural, and supportive language that feels both caring and respectful.
- When appropriate, offer suggestions for self-care, such as engaging in physical activities (like sports, walking, or yoga), hobbies, or mindfulness exercises to help improve mood.
- Encourage further reflection by asking open-ended questions.
- Provide practical advice in a gentle manner, but emphasize that your advice is informational only.
- If the user expresses severe distress or suicidal thoughts, advise them to immediately contact trusted individuals or emergency services.

Conversation History:
{history}

User: {input}
Hunter Schafer:
"""
)

chat_chain = LLMChain(
    llm=chat_model,
    prompt=mental_health_prompt,
    memory=memory
)   

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency: get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to log chat history
@app.post("/chat/")
def log_chat(user_id: int, user_message: str, ai_response: str, db: Session = Depends(get_db)):
    chat_entry = ChatHistory(user_id=user_id, user_message=user_message, ai_response=ai_response)
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    return chat_entry

# Endpoint for chatbot interaction
@app.post("/interact/")
def interact(user_id: int, message: str, db: Session = Depends(get_db)):
    # Optionally, load previous conversation from DB and set it in memory
    # For simplicity, we're using in-memory conversation here.
    response = chat_chain.invoke({"input": message})
    # Log chat interaction
    chat_entry = ChatHistory(user_id=user_id, user_message=message, ai_response=response["text"])
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    return {"response": response["text"], "chat_id": chat_entry.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
