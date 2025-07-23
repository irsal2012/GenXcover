from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .core.database import engine, Base
from .api.v1.api import api_router
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(f"{uploads_dir}/audio", exist_ok=True)
os.makedirs(f"{uploads_dir}/midi", exist_ok=True)
os.makedirs(f"{uploads_dir}/images", exist_ok=True)

# Mount static files for serving uploaded content
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_str)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
