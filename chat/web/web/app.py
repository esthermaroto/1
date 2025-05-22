import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# Setup project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..", "..", "..")
sys.path.insert(0, PROJECT_ROOT)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, '.env'))

# Configure Google AI API explicitly in app.py
print(f"DEBUG: GOOGLE_API_KEY value after load_dotenv in app.py: {os.getenv("GOOGLE_API_KEY")}")
genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Import RAG functions
from rag.query_embeddings import query_embeddings, generate_response_with_embeddings

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

class ChatMessage(BaseModel):
    message: str

@app.get("/")
async def read_root():
    index_html_path = os.path.join(BASE_DIR, "index.html")
    if not os.path.exists(index_html_path):
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_html_path)

@app.post("/api/chat")
async def chat(chat_message: ChatMessage):
    try:
        # Query embeddings and generate response
        docs = query_embeddings(chat_message.message)
        response_text = generate_response_with_embeddings(chat_message.message, docs)
        return {"response": response_text}
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

# ... existing code ... 