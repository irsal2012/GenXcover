#!/usr/bin/env python3
"""
Quick test script to generate a short song and verify the system works
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.music_generation.music_generator import MusicGenerator

async def test_quick_song():
    """Test quick song generation with short duration"""
    print("🎵 Testing quick song generation...")
    
    try:
        generator = MusicGenerator()
        result = await generator.generate_complete_song(
            title="Quick Test",
            genre="Pop",
            theme="Joy",
            style="Upbeat",
            voice_type="Male",
            key="C",
            tempo=120,
            duration=30,  # Very short duration for quick test
            include_audio=True,
            include_midi=True
        )
        
        print("✅ Quick song generation successful!")
        print(f"Title: {result['title']}")
        print(f"Duration: {result['duration']} seconds")
        print(f"Audio file: {result.get('audio_file_path', 'N/A')}")
        print(f"MIDI file: {result.get('midi_file_path', 'N/A')}")
        
        if 'lyrics' in result:
            print(f"Lyrics preview: {result['lyrics'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick song generation failed: {str(e)}")
        return False

async def main():
    """Run quick test"""
    print("🎼 Quick Song Generation Test")
    print("=" * 40)
    
    success = await test_quick_song()
    
    if success:
        print("\n🎉 Test passed! The music generation system is working correctly.")
        print("The 'running forever' issue has been resolved.")
        return 0
    else:
        print("\n⚠️ Test failed. There may still be issues.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
