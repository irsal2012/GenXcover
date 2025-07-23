#!/usr/bin/env python3
"""
Test script for the new "Generate Full Song from Lyrics" feature
This script demonstrates the complete workflow from lyrics generation to full song creation.
"""

import asyncio
import json
from backend.app.services.music_generation.music_generator import MusicGenerator

async def test_lyrics_to_song_workflow():
    """Test the complete workflow: generate lyrics -> generate full song from lyrics"""
    
    print("🎵 Testing the 'Generate Full Song from Lyrics' Feature")
    print("=" * 60)
    
    # Initialize the music generator
    music_generator = MusicGenerator()
    
    # Step 1: Generate lyrics only
    print("\n📝 Step 1: Generating lyrics...")
    lyrics_result = await music_generator.generate_lyrics_only(
        title="Digital Dreams",
        genre="Electronic",
        theme="Technology and Future",
        style="Futuristic",
        custom_prompt="A song about AI and human connection in the digital age"
    )
    
    print(f"✅ Lyrics generated successfully!")
    print(f"Title: {lyrics_result['metadata']['title']}")
    print(f"Genre: {lyrics_result['metadata']['genre']}")
    print(f"Word count: {lyrics_result['metadata']['word_count']}")
    print(f"Estimated duration: {lyrics_result['metadata']['estimated_duration']} seconds")
    
    print("\n📝 Generated Lyrics:")
    print("-" * 40)
    print(lyrics_result['lyrics'])
    print("-" * 40)
    
    # Step 2: Generate full song from the lyrics
    print("\n🎵 Step 2: Generating full song from lyrics...")
    song_result = await music_generator.generate_song_from_lyrics(
        lyrics=lyrics_result['lyrics'],
        title="Digital Dreams",
        genre="Electronic",
        voice_type="Female",
        key="Am",
        tempo=128,
        duration=None,  # Let it estimate from lyrics
        include_audio=True,
        include_midi=True,
        style="Futuristic"
    )
    
    print(f"✅ Full song generated successfully!")
    print(f"Title: {song_result['title']}")
    print(f"Genre: {song_result['genre']}")
    print(f"Voice Type: {song_result['voice_type']}")
    print(f"Key: {song_result['key']}")
    print(f"Tempo: {song_result['tempo']} BPM")
    print(f"Duration: {song_result['duration']} seconds")
    
    if song_result.get('midi_file_path'):
        print(f"🎹 MIDI file: {song_result['midi_file_path']}")
    
    if song_result.get('audio_file_path'):
        print(f"🔊 Audio file: {song_result['audio_file_path']}")
    
    # Display analysis results
    if song_result.get('analysis'):
        analysis = song_result['analysis']
        print(f"\n📊 Song Analysis:")
        print(f"  - Generation Quality: {analysis.get('generation_quality', 'N/A')}")
        print(f"  - Estimated Appeal: {analysis.get('estimated_appeal', 'N/A')}")
        print(f"  - Genre Consistency: {analysis.get('genre_consistency', 'N/A')}")
        
        if analysis.get('recommendations'):
            print(f"  - Recommendations:")
            for rec in analysis['recommendations']:
                print(f"    • {rec}")
    
    print("\n🎉 Test completed successfully!")
    print("The 'Generate Full Song from Lyrics' feature is working correctly.")
    
    return {
        'lyrics_result': lyrics_result,
        'song_result': song_result
    }

async def test_api_workflow():
    """Test the API workflow simulation"""
    
    print("\n🌐 Testing API Workflow Simulation")
    print("=" * 60)
    
    # Simulate the frontend API calls
    music_generator = MusicGenerator()
    
    # Step 1: Simulate lyrics generation API call
    print("\n📝 Simulating /songs/generate-lyrics API call...")
    lyrics_data = {
        "title": "Midnight City",
        "genre": "Pop",
        "theme": "Urban nightlife",
        "style": "Upbeat",
        "custom_prompt": "A song about the energy and excitement of city life at night"
    }
    
    lyrics_result = await music_generator.generate_lyrics_only(**lyrics_data)
    print("✅ Lyrics API simulation successful!")
    
    # Step 2: Simulate song from lyrics generation API call
    print("\n🎵 Simulating /songs/generate-from-lyrics API call...")
    song_data = {
        "lyrics": lyrics_result['lyrics'],
        "title": lyrics_data["title"],
        "genre": lyrics_data["genre"],
        "voice_type": "Male",
        "key": "C",
        "tempo": 120,
        "duration": 180,
        "include_audio": True,
        "include_midi": True,
        "style": lyrics_data["style"]
    }
    
    song_result = await music_generator.generate_song_from_lyrics(**song_data)
    print("✅ Song from lyrics API simulation successful!")
    
    print(f"\n📋 API Response Summary:")
    print(f"  - Lyrics generated: {len(lyrics_result['lyrics'])} characters")
    print(f"  - Song title: {song_result['title']}")
    print(f"  - Files generated: MIDI={bool(song_result.get('midi_file_path'))}, Audio={bool(song_result.get('audio_file_path'))}")
    
    return {
        'lyrics_api_result': lyrics_result,
        'song_api_result': song_result
    }

def print_feature_summary():
    """Print a summary of the implemented feature"""
    
    print("\n🎯 FEATURE IMPLEMENTATION SUMMARY")
    print("=" * 60)
    print("✅ Backend Implementation:")
    print("  • Added generate_song_from_lyrics() method to MusicGenerator")
    print("  • Added /songs/generate-from-lyrics API endpoint")
    print("  • Integrated with existing MIDI and audio generation")
    print("  • Added proper error handling and validation")
    
    print("\n✅ Frontend Implementation:")
    print("  • Added generateSongFromLyrics() API method")
    print("  • Enhanced lyrics results with 'Generate Full Song' button")
    print("  • Added music parameters form for lyrics-to-song conversion")
    print("  • Implemented editable lyrics functionality")
    print("  • Added proper loading states and error handling")
    
    print("\n✅ User Experience:")
    print("  • Two-step workflow: Generate lyrics → Generate full song")
    print("  • Ability to edit lyrics before music generation")
    print("  • Configurable music parameters (voice, key, tempo, etc.)")
    print("  • Seamless integration with existing UI")
    print("  • Responsive design for all screen sizes")
    
    print("\n🎵 Workflow:")
    print("  1. User generates lyrics using 'Lyrics Only' tab")
    print("  2. System displays generated lyrics")
    print("  3. User clicks 'Generate Full Song from These Lyrics'")
    print("  4. User configures music parameters (optional lyrics editing)")
    print("  5. System generates complete song with MIDI and audio")
    print("  6. User gets full song with lyrics, music, and audio files")

async def main():
    """Main test function"""
    try:
        # Test the core functionality
        await test_lyrics_to_song_workflow()
        
        # Test the API workflow
        await test_api_workflow()
        
        # Print feature summary
        print_feature_summary()
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting 'Generate Full Song from Lyrics' Feature Test")
    asyncio.run(main())
