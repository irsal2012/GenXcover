from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from ...core.database import get_db
from ...api.deps import get_current_active_user
from ...models.user import User as UserModel
import os
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Create upload directories if they don't exist
UPLOAD_DIR = "backend/uploads"
AUDIO_DIR = os.path.join(UPLOAD_DIR, "audio")
IMAGE_DIR = os.path.join(UPLOAD_DIR, "images")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)


@router.post("/audio")
async def upload_audio(
    file: UploadFile = File(...),
    song_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Upload audio file"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file"
            )
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.mp3'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(AUDIO_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {"file_path": file_path}
        
    except Exception as e:
        logger.error(f"Error uploading audio file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload audio file: {str(e)}"
        )


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Upload image file"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image file"
            )
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(IMAGE_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {"file_path": file_path}
        
    except Exception as e:
        logger.error(f"Error uploading image file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image file: {str(e)}"
        )
