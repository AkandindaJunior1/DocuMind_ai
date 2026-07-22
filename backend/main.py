from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, documents, chat, dashboard

# This is the core application object
app = FastAPI(
    title="DocuMind AI API",
    description="Backend for the DocuMind AI Business Assistant",
    version="1.0.0"
)

# Allow the React frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(dashboard.router)

# This is a "route" or "endpoint"
# When someone goes to http://localhost:8000/health, this code runs.
@app.get("/health")
async def health_check():
    """
    This is our very first endpoint.
    It simply checks if the server is running.
    """
    return {"status": "DocuMind AI is running!"}
