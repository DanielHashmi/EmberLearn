"""
EmberLearn Backend - Production Server

Real backend with Neon PostgreSQL, JWT authentication, Groq AI integration,
and per-user progress tracking.
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import real routers
from routers.auth import router as auth_router
from routers.chat import router as chat_router
from routers.progress import router as progress_router
from routers.execute import router as execute_router
from routers.exercises import router as exercises_router

# Import database
from database.config import engine, Base


# ==================== Configuration ====================

class Settings:
    """Application settings."""
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    
    @property
    def cors_origins_list(self) -> list:
        return [o.strip() for o in self.cors_origins.split(",")]

settings = Settings()


# ==================== Application ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print("🚀 EmberLearn Backend starting...")
    print(f"   Debug mode: {settings.debug}")
    print(f"   CORS origins: {settings.cors_origins_list}")
    
    # Database connection check
    try:
        from database.config import get_db
        print("   Database: configured")
    except Exception as e:
        print(f"   Database: error - {e}")
    
    yield
    print("👋 EmberLearn Backend shutting down...")


app = FastAPI(
    title="EmberLearn API",
    description="AI-powered Python tutoring platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(progress_router)
app.include_router(execute_router)
app.include_router(exercises_router)


# ==================== Health Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "emberlearn-api",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "agents": ["triage", "concepts", "code_review", "debug", "exercise", "progress"],
    }


# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*50)
    print("🔥 EmberLearn Backend Server")
    print("="*50)
    print(f"\n📍 API: http://localhost:{settings.port}")
    print(f"📚 Docs: http://localhost:{settings.port}/docs")
    print(f"🔄 ReDoc: http://localhost:{settings.port}/redoc")
    print("\n" + "="*50 + "\n")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
