# Audio Transcription Setup Guide

## Current Issue
The SARVAM API is currently not working properly (returning 404 errors). This guide provides alternative solutions for audio transcription.

## Solution 1: Install Whisper (Recommended)

Whisper is OpenAI's open-source speech recognition model that works locally.

### Installation
```bash
pip install openai-whisper
```

### Usage
Once installed, the system will automatically try Whisper as a fallback when SARVAM fails.

## Solution 2: Install FFmpeg + Whisper

For better audio format support, install FFmpeg alongside Whisper.

### Installation
```bash
# Install FFmpeg (Windows)
# Download from https://ffmpeg.org/download.html
# Or use chocolatey: choco install ffmpeg

# Install Whisper
pip install openai-whisper
```

## Solution 3: Fix SARVAM API

If you want to continue using SARVAM:

1. **Check API Key**: Verify your SARVAM API key is valid and not expired
2. **Update Endpoints**: The API endpoints may have changed
3. **Contact Support**: Reach out to SARVAM support for current API documentation

## Testing

After installing Whisper, restart your server and try uploading an MP4 file again. The system will:
1. Try SARVAM API first
2. Fall back to Whisper if SARVAM fails
3. Provide detailed error messages if all methods fail

## Supported Formats

- **SARVAM**: MP3, WAV, MP4, M4A, MOV, MKV
- **Whisper**: MP3, WAV, MP4, M4A, FLAC, OGG, and more

## Troubleshooting

If transcription still fails:
1. Check that the audio file is not corrupted
2. Try converting to WAV format
3. Ensure the file size is reasonable (< 100MB)
4. Check server logs for detailed error messages
