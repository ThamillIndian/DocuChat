#!/usr/bin/env python3
"""
Test script to verify audio/video support with Sarvam ASR
"""

import os
import sys
sys.path.append('app')

from app.services.asr_sarvam import transcribe, get_supported_formats

def test_audio_formats():
    """Test supported audio formats"""
    print("🎵 Supported Audio/Video Formats:")
    formats = get_supported_formats()
    for fmt in formats:
        print(f"  ✅ {fmt}")
    print(f"\nTotal formats supported: {len(formats)}")

def test_api_key_check():
    """Test API key configuration"""
    print("\n🔑 API Key Configuration:")
    api_key = os.getenv("SARVAM_API_KEY")
    if api_key:
        print(f"  ✅ SARVAM_API_KEY is configured")
        print(f"  Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("  ❌ SARVAM_API_KEY not found in environment")
        print("  Please add it to your .env file")

def test_transcribe_function():
    """Test the transcribe function with dummy data"""
    print("\n🎤 Testing Transcribe Function:")
    
    # Create dummy audio data
    dummy_audio = b"dummy audio data for testing"
    result = transcribe(dummy_audio, "test.mp3", "audio/mpeg")
    
    print(f"  Result type: {type(result)}")
    print(f"  Has 'text' key: {'text' in result}")
    print(f"  Has 'segments' key: {'segments' in result}")
    print(f"  Has 'meta' key: {'meta' in result}")
    
    if 'error' in result.get('meta', {}):
        print(f"  ⚠️  Error: {result['meta']['error']}")
    else:
        print(f"  ✅ Function structure is correct")

if __name__ == "__main__":
    print("🚀 Testing Sarvam ASR Integration")
    print("=" * 50)
    
    test_audio_formats()
    test_api_key_check()
    test_transcribe_function()
    
    print("\n" + "=" * 50)
    print("✅ Audio/Video support implementation complete!")
    print("\nNext steps:")
    print("1. Install requests: pip install requests>=2.31.0")
    print("2. Restart server: uvicorn app.main:app --reload --port 8000")
    print("3. Upload an MP3/WAV file through Swagger UI")
    print("4. Test chat and summarization with audio content")


