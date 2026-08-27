from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

from backend.app.core.config import settings
from backend.app.core.security import SecurityMiddleware
from backend.app.db.database import init_db
from backend.app.api.routes import router as api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-driven 10-Team Full-PPR Fantasy Football Engine with Live ESPN Sync, Dynamic VORP, Lineup Optimizer, and Waiver Arbitrage."
)

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)
app.add_middleware(SecurityMiddleware)

# Initialize Database
@app.on_event("startup")
def on_startup():
    init_db()

# Mount API routes
app.include_router(api_router, prefix="/api/v1")

# Mount Static Frontend
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
