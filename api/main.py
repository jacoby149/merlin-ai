
from fastapi import FastAPI
from chat_router import router as chat_router

app = FastAPI(title="ChatGPT-like API with Router")

# Include the chat router.
app.include_router(chat_router)

# You can also define additional routers or endpoints here.
