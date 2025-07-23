#!/usr/bin/env python3
"""
Test script for MusicGen integration
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('backend')

from app.services.music_generation.musicgen_synthesizer import MusicGenSynthesizer
from app.services.music_generation.music_generator import MusicGenerator


async def test_musicgen_availability():
    """Test if MusicGen is available"""
    print("🔍 Testing MusicGen availability...")
    
    synthesizer = MusicGenSynthesizer()
    
    if synthesizer.is_available():
        print("✅ MusicGen is available!")
        
        # Get model info
        model_info = synthesizer.get_model_info()
        print(f"📊 Model Info:")
        for key, value in model_info.items():
            print(f"   {key}: {value}")
        
        return True
    else:
        print("❌ MusicGen is not available")
        print("   Make sure you have:")
        print("   1. Installed audiocraft: pip install audiocraft")
        print("   2. PyTorch with CUDA support (recommended)")
        print("   3. Sufficient GPU memory (8GB+ recommended)")
        return False


async def test_basic_generation():
    """Test basic music generation"""
    print("\n🎵 Testing basic music generation...")
    
    synthesizer = MusicGenSynthesizer()
    
    if not synthesizer.is_available():
        print("❌ Skipping generation test - MusicGen not available")
        return
    
    try:
        # Test simple prompt generation
        result = await synthesizer.generate_from_prompt(
            prompt="upbeat pop song with piano",
            duration=5,  # Short duration for testing
            title="Test Song"
        )
        
        print("✅ Basic generation successful!")
        print(f"   Generated file: {result['audio_file_path']}")
        print(f"   Duration: {result['duration']:.2f} seconds")
        print(f"   Model: {result['model']}")
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")


async def test_music_generator_integration():
    """Test MusicGenerator with MusicGen"""
    print("\n🎼 Testing MusicGenerator integration...")
    
    try:
        # Initialize with MusicGen
        generator = MusicGenerator(use_musicgen=True)
        
        if generator.using_musicgen:
            print("✅ MusicGenerator is using MusicGen!")
        else:
            print("⚠️  MusicGenerator fell back to basic synthesizer")
        
        # Test instrumental generation
        print("   Testing instrumental generation...")
        result = await generator.generate_instrumental(
            title="Test Instrumental",
            genre="Pop",
            key="C",
            tempo=120,
            duration=8,  # Short for testing
            include_audio=True
        )
        
        print("✅ Instrumental generation successful!")
        print(f"   Audio file: {result.get('audio_file_path', 'Not generated')}")
        
    except Exception as e:
        print(f"❌ MusicGenerator integration failed: {e}")


async def test_requirements():
    """Test if all required packages are installed"""
    print("\n📦 Testing package requirements...")
    
    required_packages = [
        'torch',
        'torchaudio',
        'audiocraft',
        'transformers',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r backend/requirements-musicgen.txt")
        return False
    else:
        print("\n✅ All required packages are installed!")
        return True


async def main():
    """Main test function"""
    print("🚀 MusicGen Integration Test")
    print("=" * 50)
    
    # Test requirements
    requirements_ok = await test_requirements()
    
    if not requirements_ok:
        print("\n❌ Please install missing requirements first")
        return
    
    # Test MusicGen availability
    musicgen_available = await test_musicgen_availability()
    
    if musicgen_available:
        # Test basic generation
        await test_basic_generation()
        
        # Test integration
        await test_music_generator_integration()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    
    if musicgen_available:
        print("✅ MusicGen integration is working!")
        print("\nNext steps:")
        print("1. Install requirements: pip install -r backend/requirements-musicgen.txt")
        print("2. Restart your backend server")
        print("3. Test music generation through the API")
    else:
        print("❌ MusicGen integration needs setup")
        print("\nSetup steps:")
        print("1. Install audiocraft: pip install audiocraft")
        print("2. Install PyTorch with CUDA: pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118")
        print("3. Ensure you have sufficient GPU memory (8GB+ recommended)")


if __name__ == "__main__":
    asyncio.run(main())
