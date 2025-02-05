import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai

# Ensure your OpenAI API key is set in the environment.
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise Exception("Missing OpenAI API key. Please set the OPENAI_API_KEY environment variable.")

# Create a router instance.
router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory store for conversation histories keyed by session_id.
conversations = {}

# -------------------------------
# Pydantic Models
# -------------------------------

class ChatRequest(BaseModel):
    session_id: str = "default"  # Use "default" if no session_id is provided.
    message: str

class ChatResponse(BaseModel):
    reply: str

class HistoryResponse(BaseModel):
    session_id: str
    history: list

# -------------------------------
# Endpoints
# -------------------------------

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Send a message to the chatbot and receive a reply.
    The conversation history is maintained per session.
    """
    # Initialize conversation history for new sessions.
    if req.session_id not in conversations:
        conversations[req.session_id] = []

    conversation_history = conversations[req.session_id]

    # Append the user's message to the conversation history.
    conversation_history.append({"role": "user", "content": req.message})

    # Call the OpenAI ChatCompletion API with the conversation history.
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or any available model
            messages=conversation_history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    # Extract the assistant's reply.
    reply_message = response["choices"][0]["message"]["content"]

    # Append the assistant's reply to the conversation history.
    conversation_history.append({"role": "assistant", "content": reply_message})

    return ChatResponse(reply=reply_message)

@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    """
    Retrieve the conversation history for the given session.
    """
    if session_id not in conversations:
        raise HTTPException(status_code=404, detail="Session not found")
    return HistoryResponse(session_id=session_id, history=conversations[session_id])

@router.delete("/history/{session_id}")
async def reset_history(session_id: str):
    """
    Delete the conversation history for the specified session.
    """
    if session_id in conversations:
        del conversations[session_id]
    return {"detail": f"History for session '{session_id}' has been reset."}

