"""
    commands.py
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from endpoints.commands.endpoints import read_main_py,write_main_py,read_app_js,write_app_js
from openai import OpenAI
import settings
import re

# Create a router instance.
router = APIRouter(prefix="/auto_coder", tags=["auto_coder"])

# Initialize the OpenAI client.
client = OpenAI(api_key=settings.OPENAPI_KEY)

if not client.api_key:
    raise Exception("Missing OpenAI API key. Please set the OPENAPI_API_KEY environment variable.")


import re
from fastapi import HTTPException

def ask_api(prompt: str):
    """
    Sends the prompt to the GPT-4o mini model and extracts the modified code
    (enclosed between <|start-code|> and <|end-code|>) and any additional explanatory reply.
    """
    conversation_history = [{"role": "user", "content": prompt}]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or any available model
            messages=conversation_history,
            temperature=0.5,      # adjust as needed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API request failed: {e}")

    full_response = response.choices[0].message.content

    # Use a regex to find the text enclosed in our custom tokens.
    pattern = r"<\|start-code\|>(.*?)<\|end-code\|>"
    match = re.search(pattern, full_response, re.DOTALL)
    if match:
        code_block = match.group(1).strip()
        # Remove the code block from the full response to form the reply text.
        reply_text = re.sub(pattern, '', full_response, flags=re.DOTALL).strip()
    else:
        code_block = ""
        reply_text = full_response.strip()

    return code_block, reply_text

class APIModRequest(BaseModel):
    chat:str
    context:str

class APIModRespose(BaseModel):
    reply:str

@router.post("/api_mod")
async def api_mod(r:APIModRequest):
    """
    Modifies the main.py file
    """
    preface = "Here is a main.py for a fastapi implementation!"
    main_py = await read_main_py()
    main_py = main_py["content"]
    chat = r.chat
    code = "Answer with a modified version of main.py surrounded by <|start-code|> and <|end-code|>. the output is being written right over the file!!!!"
    exp = "Anything in the reply not encapsulated in <|start-code|> and <|end-code|> will be shown to a user to explain the changes!"
    prompt = "\n".join([preface,main_py,chat,code,exp])
    code,reply = ask_api(prompt)
    await write_main_py(code)
    return {"reply":reply}


def ask_ui(prompt: str):
    """
    Sends the prompt to the GPT-4o mini model and extracts the modified code
    (enclosed between <|start-code|> and <|end-code|>) and any additional explanatory reply.
    """
    conversation_history = [{"role": "user", "content": prompt}]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or any available model
            messages=conversation_history,
            temperature=0.5,      # adjust as needed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API request failed: {e}")

    full_response = response.choices[0].message.content

    # Use a regex to find the text enclosed in our custom tokens.
    pattern = r"<\|start-code\|>(.*?)<\|end-code\|>"
    match = re.search(pattern, full_response, re.DOTALL)
    if match:
        code_block = match.group(1).strip()
        # Remove the code block from the full response to form the reply text.
        reply_text = re.sub(pattern, '', full_response, flags=re.DOTALL).strip()
    else:
        code_block = ""
        reply_text = full_response.strip()

    return code_block, reply_text

class APIModRequest(BaseModel):
    chat:str
    context:str

class UIModResponse(BaseModel):
    reply:str

@router.post("/ui_mod")
async def ui_mod(r:APIModRequest):
    """
    Modifies the App.js file
    """
    api_preface="Here is a main.py for a fastapi implementation"
    main_py = await read_main_py()
    main_py = main_py["content"]
 
    preface = "Here is a App.js for a React implementation!"
    app_js = await read_app_js()
    app_js = app_js["content"]

    chat = r.chat
    code = "Answer with a modified version of App.js surrounded by <|start-code|> and <|end-code|>. the output is being written right over the file!!!!"
    exp = "Anything in the reply not encapsulated in <|start-code|> and <|end-code|> will be shown to a user to explain the changes!"
    prompt = "\n".join([api_preface,main_py,preface,app_js,chat,code,exp])
    code,reply = ask_api(prompt)
    await write_app_js(code)
    return {"reply":reply}

