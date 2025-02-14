
import os
import uuid
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import settings

# Initialize the OpenAI client.
client = OpenAI(api_key=settings.OPENAPI_KEY)
if not client.api_key:
    raise Exception("Missing OpenAI API key. Please set the OPENAPI_API_KEY environment variable.")

# Create a router instance.
router = APIRouter(prefix="/chat", tags=["chat"])

# Define the SQLite database file.
DATABASE = "chat_sessions.db"

# -------------------------------
# SQLite Database Utilities
# -------------------------------

def get_db_connection():
    """Returns a SQLite connection with row factory set."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with the required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create a table to store session info.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Create a table to store conversation messages.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)
    conn.commit()
    conn.close()

# Initialize the database when the module is imported.
init_db()

# -------------------------------
# Pydantic Models
# -------------------------------

class ChatRequest(BaseModel):
    session_id: str = "default"  # If "default", a new session will be created.
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str

class HistoryResponse(BaseModel):
    session_id: str
    history: list

class SessionInfo(BaseModel):
    session_id: str
    created_at: str

class SessionsResponse(BaseModel):
    sessions: list[SessionInfo]

# -------------------------------
# Endpoints
# -------------------------------

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Send a message to the chatbot and receive a reply.
    
    This endpoint:
      - Creates a new session (if needed) or reuses an existing one.
      - Stores the user's message in SQLite.
      - Loads the full conversation history for that session.
      - Passes the conversation history (without any session IDs) to the OpenAI API.
      - Stores the assistant’s reply in SQLite.
    """
    # Use the provided session_id or generate a new one if "default".
    session_id = req.session_id if req.session_id != "default" else str(uuid.uuid4())

    # Open a database connection.
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create a new session in the database if it doesn't already exist.
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO sessions (session_id) VALUES (?)", (session_id,))
        conn.commit()

    # Store the user's message.
    cursor.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, "user", req.message)
    )
    conn.commit()

    # Load the entire conversation history for this session (ordered by time).
    cursor.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at ASC",
        (session_id,)
    )
    conversation_history = [
        {"role": row["role"], "content": row["content"]}
        for row in cursor.fetchall()
    ]
    conn.close()

    # Call the OpenAI API using the conversation history.
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or any available model
            messages=conversation_history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    # Extract the assistant's reply.
    reply_message = response.choices[0].message.content

    # Store the assistant's reply in the database.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, "assistant", reply_message)
    )
    conn.commit()
    conn.close()

    return ChatResponse(session_id=session_id, reply=reply_message)

@router.get("/sessions", response_model=SessionsResponse)
async def get_sessions():
    """
    Retrieve a list of all sessions with their creation timestamps.
    
    This endpoint allows a client to view all available sessions stored in SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT session_id, created_at FROM sessions ORDER BY created_at DESC")
    sessions = [
        {"session_id": row["session_id"], "created_at": row["created_at"]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return SessionsResponse(sessions=sessions)

@router.get("/sessions/{session_id}", response_model=HistoryResponse)
async def load_session(session_id: str):
    """
    Retrieve the conversation history for the specified session.
    
    This endpoint loads the conversation messages for a given session from SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify that the session exists.
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Session not found")

    cursor.execute(
        "SELECT role, content, created_at FROM messages WHERE session_id = ? ORDER BY created_at ASC",
        (session_id,)
    )
    history = [
        {"role": row["role"], "content": row["content"], "created_at": row["created_at"]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return HistoryResponse(session_id=session_id, history=history)

@router.delete("/sessions/{session_id}")
async def reset_session(session_id: str):
    """
    Delete the conversation history and session from SQLite.
    
    This endpoint allows a user to completely reset a session.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
    return {"detail": f"Session '{session_id}' has been reset."}

