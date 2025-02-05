
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Auto Code This API",
    description="Visit localhost:3001 to code this API automatically",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health_check",  description="Returns a health status. You can ttry asking the ai chat to make this endpoint return the health of the mongodb connection!")
def health_check():
    return {"Hello": "World"}
