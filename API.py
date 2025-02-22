import os
from dotenv import load_dotenv, find_dotenv
from langchain.memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv(find_dotenv())

# Load API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Check your .env file.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini Model
chat_model = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7  # Adjust temperature for response creativity
)

# Use the new Message History class
message_history = ChatMessageHistory()

# New memory-aware chatbot using RunnableWithMessageHistory
chat_chain = RunnableWithMessageHistory(chat_model, lambda session_id: message_history)

# FastAPI app setup
app = FastAPI()

class ChatRequest(BaseModel):
    user_input: str
    session_id: str  # Track session to manage conversation history

@app.post("/chat/")
async def chat_with_bot(request: ChatRequest):
    try:
        # Generate response while maintaining conversation history
        response = chat_chain.invoke(input=request.user_input, config={"configurable": {"session_id": request.session_id}})
        
        # Retrieve updated chat history
        chat_history = message_history.messages

        return {
            "user_input": request.user_input,
            "response": response,
            "chat_history": chat_history  # Return past conversation history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ensure API runs properly when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("API:app", host="127.0.0.1", port=8000, reload=True)
