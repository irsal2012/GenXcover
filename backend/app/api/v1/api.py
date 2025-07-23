from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .songs import router as songs_router
from .upload import router as upload_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(songs_router, prefix="/songs", tags=["songs"])
api_router.include_router(upload_router, prefix="/upload", tags=["upload"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "GenXcover API"}
