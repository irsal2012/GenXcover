#!/usr/bin/env python3
"""
Simple test script to verify the backend is working correctly.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_backend():
    """Test basic backend functionality"""
    print("🚀 Testing GenXcover Backend...")
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from app.main import app
        from app.core.config import settings
        from app.models.user import User
        from app.models.song import Song
        from app.services.auth import AuthService
        print("✅ All imports successful")
        
        # Test configuration
        print("⚙️  Testing configuration...")
        print(f"   App name: {settings.app_name}")
        print(f"   Version: {settings.version}")
        print(f"   Debug mode: {settings.debug}")
        print(f"   Database URL: {settings.database_url}")
        print("✅ Configuration loaded successfully")
        
        # Test database models
        print("🗄️  Testing database models...")
        print(f"   User table: {User.__tablename__}")
        print(f"   Song table: {Song.__tablename__}")
        print("✅ Database models loaded successfully")
        
        # Test FastAPI app
        print("🌐 Testing FastAPI app...")
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
        print("✅ FastAPI app initialized successfully")
        
        print("\n🎉 Backend test completed successfully!")
        print("🔗 You can now run the server with:")
        print("   uvicorn app.main:app --reload")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_openai_config():
    """Test OpenAI configuration"""
    print("\n🤖 Testing OpenAI configuration...")
    
    try:
        from app.core.config import settings
        
        if settings.openai_api_key:
            print("✅ OpenAI API key is configured")
            # Don't print the actual key for security
            key_preview = settings.openai_api_key[:10] + "..." if len(settings.openai_api_key) > 10 else "***"
            print(f"   Key preview: {key_preview}")
        else:
            print("⚠️  OpenAI API key not configured")
            print("💡 Set OPENAI_API_KEY in your .env file for lyrics generation")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking OpenAI config: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🎵 GenXcover Backend Test Suite")
    print("=" * 60)
    
    # Run async test
    success = asyncio.run(test_backend())
    
    # Test OpenAI config
    test_openai_config()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Backend is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Start the backend: uvicorn app.main:app --reload")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Test the API endpoints")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
