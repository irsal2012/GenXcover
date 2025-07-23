# MusicGen Integration Setup Guide

This guide will help you integrate Facebook's MusicGen into your application for high-quality music generation, replacing the basic synthesizer.

## Overview

**What is MusicGen?**
- Facebook's state-of-the-art music generation model
- Generates high-quality instrumental music from text descriptions
- Open-source and self-hostable
- Significantly better audio quality than basic synthesis

**Current vs New System:**
- **Before**: Basic waveform synthesis (poor quality)
- **After**: AI-generated music with MusicGen (professional quality)

## Prerequisites

### System Requirements
- **GPU**: NVIDIA GPU with 8GB+ VRAM (recommended)
- **RAM**: 16GB+ system RAM
- **Storage**: 10GB+ free space for model weights
- **Python**: 3.8+
- **CUDA**: Compatible CUDA installation (if using GPU)

### Check Your System
```bash
# Check GPU
nvidia-smi

# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

## Installation Steps

### 1. Install MusicGen Dependencies

```bash
# Navigate to backend directory
cd backend

# Install MusicGen requirements
pip install -r requirements-musicgen.txt

# Or install manually:
pip install audiocraft==1.3.0
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Test Installation

```bash
# Run the integration test
python ../test_musicgen_integration.py
```

Expected output:
```
🚀 MusicGen Integration Test
==================================================
📦 Testing package requirements...
✅ torch
✅ torchaudio
✅ audiocraft
✅ transformers
✅ numpy

✅ All required packages are installed!

🔍 Testing MusicGen availability...
✅ MusicGen is available!
📊 Model Info:
   available: True
   model_name: musicgen-medium
   device: cuda
   sample_rate: 32000
   channels: 1
   max_duration: 30
   cuda_available: True
```

### 3. Update Your Application

The integration is already implemented! The `MusicGenerator` class will automatically use MusicGen if available:

```python
# In your code, this will now use MusicGen automatically
from app.services.music_generation.music_generator import MusicGenerator

generator = MusicGenerator(use_musicgen=True)
```

## Usage Examples

### Basic Music Generation
```python
# Generate instrumental music
result = await generator.generate_instrumental(
    title="My Song",
    genre="Pop",
    key="C",
    tempo=120,
    duration=15,  # seconds
    style="upbeat"
)

print(f"Generated: {result['audio_file_path']}")
```

### Direct Prompt Generation
```python
# Generate from text description
from app.services.music_generation.musicgen_synthesizer import MusicGenSynthesizer

synthesizer = MusicGenSynthesizer()
result = await synthesizer.generate_from_prompt(
    prompt="upbeat electronic dance music with synthesizers",
    duration=10,
    title="EDM Track"
)
```

### Complete Song Generation
```python
# Generate complete song (lyrics + music)
result = await generator.generate_complete_song(
    title="My New Song",
    genre="Rock",
    theme="Freedom",
    tempo=140,
    duration=20,
    include_audio=True
)
```

## Configuration Options

### Model Selection
You can choose different MusicGen models:

```python
# In musicgen_synthesizer.py, change model_name:
self.model_name = 'musicgen-small'   # Faster, lower quality
self.model_name = 'musicgen-medium'  # Balanced (default)
self.model_name = 'musicgen-large'   # Best quality, slower
```

### Generation Parameters
```python
# Adjust generation settings
synthesizer.set_generation_params(
    duration=15,        # Max 30 seconds
    temperature=1.0,    # Creativity (0.1-2.0)
    top_k=250,         # Sampling parameter
    cfg_coef=3.0       # Classifier-free guidance
)
```

## Performance Optimization

### GPU Memory Management
```python
# For limited GPU memory, use smaller model
self.model_name = 'musicgen-small'

# Or reduce batch size in generation
```

### CPU Fallback
If no GPU is available, MusicGen will run on CPU (much slower):
```python
# The system automatically detects and uses CPU if needed
# Generation will take 5-10x longer
```

## Troubleshooting

### Common Issues

**1. "MusicGen model not available"**
```bash
# Check installation
pip list | grep audiocraft
pip install audiocraft

# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

**2. "CUDA out of memory"**
```python
# Use smaller model
self.model_name = 'musicgen-small'

# Or reduce duration
duration = 8  # Instead of 30
```

**3. "Model loading takes too long"**
- First load downloads ~1.5GB model weights
- Subsequent loads are faster
- Consider using smaller model for development

**4. "Audio quality still poor"**
- Ensure MusicGen is actually being used (check logs)
- Verify test script shows "✅ MusicGen is available!"
- Check that `using_musicgen = True` in MusicGenerator

### Debug Commands
```bash
# Test MusicGen directly
python -c "
from audiocraft.models import MusicGen
model = MusicGen.get_pretrained('musicgen-medium')
print('MusicGen loaded successfully!')
"

# Check GPU usage during generation
nvidia-smi -l 1
```

## API Integration

The existing API endpoints will automatically use MusicGen:

```bash
# Test through API
curl -X POST "http://localhost:8000/api/v1/songs/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Song",
    "genre": "Pop",
    "tempo": 120,
    "duration": 10
  }'
```

## Quality Comparison

### Before (Basic Synthesizer)
- ❌ Artificial sine/sawtooth waves
- ❌ Poor vocal synthesis
- ❌ No realistic instruments
- ❌ Basic mixing

### After (MusicGen)
- ✅ AI-generated realistic music
- ✅ Professional sound quality
- ✅ Multiple instruments and styles
- ✅ Proper audio mastering

## Next Steps

1. **Install dependencies**: `pip install -r backend/requirements-musicgen.txt`
2. **Run test script**: `python test_musicgen_integration.py`
3. **Restart backend server**
4. **Test through your application**
5. **Monitor GPU usage and performance**

## Advanced Configuration

### Custom Model Path
```python
# Use local model files
model = MusicGen.get_pretrained('/path/to/local/model')
```

### Batch Generation
```python
# Generate multiple tracks at once
descriptions = ["pop song", "rock song", "jazz song"]
wavs = model.generate(descriptions)
```

### Audio Post-Processing
```python
# The synthesizer includes automatic:
# - Loudness normalization
# - Dynamic range compression
# - Format conversion
```

## Support

If you encounter issues:

1. Check the test script output
2. Verify GPU/CUDA setup
3. Review system requirements
4. Check MusicGen documentation: https://github.com/facebookresearch/audiocraft

The integration provides automatic fallback to the basic synthesizer if MusicGen is unavailable, ensuring your application continues to work.
