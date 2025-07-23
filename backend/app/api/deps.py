from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import verify_token
from ..services.auth import AuthService
from ..models.user import User

security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user - TEMPORARILY DISABLED"""
    # Create a dummy user for testing without authentication
    dummy_user = User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    return dummy_user


def get_current_active_user(db: Session = Depends(get_db)) -> User:
    """Get current active user - TEMPORARILY DISABLED"""
    # Create a dummy user for testing without authentication
    dummy_user = User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    return dummy_user


def get_current_superuser(db: Session = Depends(get_db)) -> User:
    """Get current superuser - TEMPORARILY DISABLED"""
    # Create a dummy superuser for testing without authentication
    dummy_user = User(
        id=1,
        email="admin@example.com",
        full_name="Admin User",
        is_active=True,
        is_superuser=True
    )
    return dummy_user
