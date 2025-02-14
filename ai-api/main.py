
from fastapi import FastAPI
from endpoints.chat.endpoints import router as chat_router
from endpoints.commands.endpoints import router as commands_router
from endpoints.auto_coder.endpoints import router as auto_router

from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="ChatGPT-like API with Router")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the chat router.
app.include_router(chat_router)
app.include_router(commands_router)
app.include_router(auto_router)

# You can also define additional routers or endpoints here.
