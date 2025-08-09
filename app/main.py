from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from app.api.v1.endpoints import router
from app.utils.logging_config import setup_logging

load_dotenv()
setup_logging()

app = FastAPI(
    title="Bajaj Hackathon Query-Retrieval System",
    description="LLM-powered document analysis and decision making",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Include router without authentication
app.include_router(router, prefix="/api/v1/hackrx")

@app.get("/")
async def root():
    return {"message": "Bajaj Hackathon API is running", "status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)