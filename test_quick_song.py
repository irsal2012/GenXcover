#!/usr/bin/env python3
"""
Quick test for solo guitar song generation to test performance
"""

import asyncio
import sys
import os
import time

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.music_generation.music_generator import MusicGenerator

async def test_solo_guitar_generation():
    """Test solo guitar song generation with performance timing"""
    print("🎸 Testing solo guitar song generation...")
    
    start_time = time.time()
    
    try:
        generator = MusicGenerator()
        
        # Generate song similar to what was shown in the image
        result = await generator.generate_complete_song(
            title="Solo Guitar Song",
            genre="Rock",
            theme="Freedom",
            style="Melodic",
            voice_type="Male",
            key="G",
            tempo=120,
            duration=60,  # Shorter duration for faster testing
            include_audio=True,
            include_midi=True,
            custom_prompt="solo guitar"
        )
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        print("✅ Solo guitar song generation successful!")
        print(f"⏱️  Generation time: {generation_time:.2f} seconds")
        print(f"🎵 Title: {result['title']}")
        print(f"🎸 Genre: {result['genre']}")
        print(f"⏰ Duration: {result['duration']} seconds")
        print(f"📝 Has lyrics: {'lyrics' in result}")
        print(f"🎹 Has MIDI: {'midi_file_path' in result}")
        print(f"🔊 Has audio: {'audio_file_path' in result}")
        
        if 'lyrics' in result:
            print("\n📝 Generated lyrics preview:")
            print("-" * 40)
            lyrics_preview = result['lyrics'][:200] + "..." if len(result['lyrics']) > 200 else result['lyrics']
            print(lyrics_preview)
            print("-" * 40)
        
        if 'analysis' in result:
            analysis = result['analysis']
            print(f"\n📊 Quality Analysis:")
            print(f"   Quality score: {analysis.get('generation_quality', 'N/A')}")
            print(f"   Appeal score: {analysis.get('estimated_appeal', 'N/A')}")
            print(f"   Complexity: {analysis.get('complexity_score', 'N/A')}")
        
        # Performance assessment
        if generation_time < 5:
            print(f"🚀 Performance: EXCELLENT (under 5 seconds)")
        elif generation_time < 15:
            print(f"✅ Performance: GOOD (under 15 seconds)")
        elif generation_time < 30:
            print(f"⚠️  Performance: ACCEPTABLE (under 30 seconds)")
        else:
            print(f"❌ Performance: SLOW (over 30 seconds)")
        
        return True
        
    except Exception as e:
        end_time = time.time()
        generation_time = end_time - start_time
        print(f"❌ Solo guitar generation failed after {generation_time:.2f} seconds: {str(e)}")
        return False

async def test_instrumental_only():
    """Test instrumental-only generation for comparison"""
    print("\n🎼 Testing instrumental-only generation...")
    
    start_time = time.time()
    
    try:
        generator = MusicGenerator()
        
        result = await generator.generate_instrumental(
            title="Solo Guitar Instrumental",
            genre="Rock",
            key="G",
            tempo=120,
            duration=60,
            style="Melodic",
            include_audio=True
        )
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        print("✅ Instrumental generation successful!")
        print(f"⏱️  Generation time: {generation_time:.2f} seconds")
        print(f"🎵 Title: {result['title']}")
        print(f"🎹 Has MIDI: {'midi_file_path' in result}")
        print(f"🔊 Has audio: {'audio_file_path' in result}")
        
        return True
        
    except Exception as e:
        end_time = time.time()
        generation_time = end_time - start_time
        print(f"❌ Instrumental generation failed after {generation_time:.2f} seconds: {str(e)}")
        return False

async def main():
    """Run performance tests"""
    print("🎸 Solo Guitar Performance Test")
    print("=" * 50)
    
    total_start = time.time()
    
    # Test complete song generation
    test1_result = await test_solo_guitar_generation()
    
    # Test instrumental only
    test2_result = await test_instrumental_only()
    
    total_end = time.time()
    total_time = total_end - total_start
    
    print("\n" + "=" * 50)
    print("🎸 Performance Test Results")
    print("=" * 50)
    
    print(f"Complete Song Generation: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"Instrumental Generation: {'✅ PASSED' if test2_result else '❌ FAILED'}")
    print(f"Total Test Time: {total_time:.2f} seconds")
    
    if test1_result and test2_result:
        print("🎉 All performance tests passed!")
        if total_time < 10:
            print("🚀 Overall performance: EXCELLENT")
        elif total_time < 30:
            print("✅ Overall performance: GOOD")
        else:
            print("⚠️  Overall performance: Could be improved")
        return 0
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
