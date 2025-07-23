#!/usr/bin/env python3
"""
Simple test script to verify music generation functionality
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.music_generation.music_generator import MusicGenerator
from app.services.music_generation.lyrics_generator import LyricsGenerator
from app.services.music_generation.midi_generator import MIDIGenerator
from app.services.music_generation.audio_synthesizer import AudioSynthesizer

async def test_lyrics_generation():
    """Test lyrics generation"""
    print("🎤 Testing lyrics generation...")
    
    try:
        generator = LyricsGenerator()
        result = await generator.generate_lyrics(
            title="Test Song",
            genre="Pop",
            theme="Love",
            style="Upbeat"
        )
        
        print("✅ Lyrics generation successful!")
        print(f"Title: {result['metadata']['title']}")
        print(f"Genre: {result['metadata']['genre']}")
        print(f"Word count: {result['metadata']['word_count']}")
        print(f"Estimated duration: {result['metadata']['estimated_duration']} seconds")
        print("\nGenerated lyrics:")
        print("-" * 50)
        print(result['lyrics'])
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Lyrics generation failed: {str(e)}")
        return False

async def test_midi_generation():
    """Test MIDI generation"""
    print("\n🎹 Testing MIDI generation...")
    
    try:
        generator = MIDIGenerator()
        result = await generator.generate_midi(
            title="Test Instrumental",
            genre="Pop",
            key="C",
            tempo=120,
            duration=60
        )
        
        print("✅ MIDI generation successful!")
        print(f"MIDI file: {result['midi_file_path']}")
        print(f"Key: {result['generation_info']['key']}")
        print(f"Tempo: {result['generation_info']['tempo']}")
        print(f"Chord progression: {result['generation_info']['chord_progression']}")
        
        return True
        
    except Exception as e:
        print(f"❌ MIDI generation failed: {str(e)}")
        return False

async def test_audio_synthesis():
    """Test audio synthesis"""
    print("\n🔊 Testing audio synthesis...")
    
    try:
        # First generate MIDI
        midi_generator = MIDIGenerator()
        midi_result = await midi_generator.generate_midi(
            title="Test Audio",
            genre="Pop",
            key="C",
            tempo=120,
            duration=30  # Short duration for testing
        )
        
        # Then synthesize audio
        synthesizer = AudioSynthesizer()
        audio_result = await synthesizer.synthesize_audio(
            midi_data=midi_result['midi_data'],
            lyrics=None,  # No vocals for this test
            voice_type='Male',
            output_format='wav'
        )
        
        print("✅ Audio synthesis successful!")
        print(f"Audio file: {audio_result['audio_file_path']}")
        print(f"Duration: {audio_result['duration']} seconds")
        print(f"Sample rate: {audio_result['sample_rate']} Hz")
        print(f"Channels: {audio_result['channels']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio synthesis failed: {str(e)}")
        return False

async def test_complete_song_generation():
    """Test complete song generation"""
    print("\n🎵 Testing complete song generation...")
    
    try:
        generator = MusicGenerator()
        result = await generator.generate_complete_song(
            title="Complete Test Song",
            genre="Pop",
            theme="Happiness",
            style="Upbeat",
            voice_type="Male",
            key="C",
            tempo=120,
            duration=60,  # Short duration for testing
            include_audio=True,
            include_midi=True
        )
        
        print("✅ Complete song generation successful!")
        print(f"Title: {result['title']}")
        print(f"Genre: {result['genre']}")
        print(f"Duration: {result['duration']} seconds")
        print(f"Has lyrics: {'lyrics' in result}")
        print(f"Has MIDI: {'midi_file_path' in result}")
        print(f"Has audio: {'audio_file_path' in result}")
        
        if 'analysis' in result:
            analysis = result['analysis']
            print(f"Quality score: {analysis.get('generation_quality', 'N/A')}")
            print(f"Appeal score: {analysis.get('estimated_appeal', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete song generation failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🎼 Starting Music Generation Tests")
    print("=" * 60)
    
    tests = [
        test_lyrics_generation,
        test_midi_generation,
        test_audio_synthesis,
        test_complete_song_generation
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("🎼 Test Results Summary")
    print("=" * 60)
    
    test_names = [
        "Lyrics Generation",
        "MIDI Generation", 
        "Audio Synthesis",
        "Complete Song Generation"
    ]
    
    passed = 0
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Music generation system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
