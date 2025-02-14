"""
    commands.py
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from endpoints.commands.endpoints import read_main_py,write_main_py
import settings

# Create a router instance.
router = APIRouter(prefix="/auto_coder", tags=["auto_coder"])

class APIModRequest:
    chat:str
    context:str

class APIModResponse:
    reply:str

@router.post("/api_mod")
async def api_mod(r:APIModRequest):
    """
    Modifies the main.py file
    """
    preface = "Here is a main.py for a fastapi implementation!"
    main_py = await read_main_py()
    chat = r.chat
    code = "Answer with a main.py surrounded by $$$ $$$. the output is being loaded right in!!!!"
    exp = "Anything in the reply not encapsulated in $$$ $$$ will be shown to a user to explain the changes!"
    prompt = "\n".join([preface,main_py,chat,code,exp])
    code,reply = ask(prompt)
    await write_main_py(code)
    return reply

@router.post("/api_mod")
async def ui_mod(r:APIModRequest):
    """
    Modifies the main.py file
    """
    preface = "Here is a main.py for a fastapi implementation!"
    main_py = await read_main_py()
    chat = r.chat
    code = "Answer with a main.py surrounded by $$$ $$$. the output is being loaded right in!!!!"
    exp = "Anything in the reply not encapsulated in $$$ $$$ will be shown to a user to explain the changes!"
    prompt = "\n".join([preface,main_py,chat,code,exp])
    code,reply = ask(prompt)
    await write_main_py(code)
    return reply
