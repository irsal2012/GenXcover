from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .songs import router as songs_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(songs_router, prefix="/songs", tags=["songs"])
