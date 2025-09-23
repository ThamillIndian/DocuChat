import os
import json
from typing import Dict, Any
from .asr_fallback import transcribe_with_whisper, transcribe_with_ffmpeg_whisper

# Safe import for requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

def transcribe(file_bytes: bytes, filename: str, mime: str) -> dict:
    """
    Transcribe audio/video using Sarvam AI Speech-to-Text API
    Supports both Real-time API (for short files) and Batch API (for longer files)
    """
    # Check if requests module is available
    if not REQUESTS_AVAILABLE:
        return {
            "text": f"[SARVAM-ASR: requests module not available for {filename}. Using fallback transcription.]",
            "segments": [],
            "lang": "auto",
            "meta": {"filename": filename, "mime": mime, "error": "requests_not_available"}
        }
    
    api_key = os.getenv("SARVAM_API_KEY")
    
    if not api_key:
        return {
            "text": f"[SARVAM-ASR: API key not configured for {filename}. Please set SARVAM_API_KEY in your environment variables.]",
            "segments": [],
            "lang": "auto",
            "meta": {"filename": filename, "mime": mime, "error": "no_api_key"}
        }
    
    try:
        # Determine file size to choose appropriate API
        file_size_mb = len(file_bytes) / (1024 * 1024)
        
        # For very large files (>10MB), provide a warning
        if file_size_mb > 10:
            return {
                "text": f"[SARVAM-ASR: File too large ({file_size_mb:.1f}MB) for processing. Please use a smaller file (<10MB)]",
                "segments": [],
                "lang": "auto",
                "meta": {"filename": filename, "mime": mime, "error": "file_too_large", "size_mb": file_size_mb}
            }
        
        # Try real-time API first for all files
        result = _transcribe_realtime(file_bytes, filename, mime, api_key)
        
        # If real-time fails, try batch
        if 'error' in result.get('meta', {}):
            batch_result = _transcribe_batch(file_bytes, filename, mime, api_key)
            # If batch also fails, try fallback methods
            if 'error' in batch_result.get('meta', {}):
                # Try Whisper fallback first
                whisper_result = transcribe_with_whisper(file_bytes, filename, mime)
                if 'error' not in whisper_result.get('meta', {}):
                    return whisper_result
                
                # Try FFmpeg + Whisper fallback
                ffmpeg_result = transcribe_with_ffmpeg_whisper(file_bytes, filename, mime)
                if 'error' not in ffmpeg_result.get('meta', {}):
                    return ffmpeg_result
                
                # If all methods fail, return comprehensive error message
                return {
                    "text": f"[TRANSCRIPTION FAILED: Unable to transcribe {filename} using any available method.\n\nSARVAM API Issues:\n- Both real-time and batch APIs failed\n- This could be due to invalid/expired API key, service issues, or network problems\n\nFallback Methods Failed:\n- Whisper: {whisper_result['meta'].get('error', 'Unknown error')}\n- FFmpeg+Whisper: {ffmpeg_result['meta'].get('error', 'Unknown error')}\n\nRecommendations:\n1. Check your SARVAM API key\n2. Try a different audio file format (WAV, MP3)\n3. Install Whisper locally: pip install openai-whisper\n4. Install FFmpeg for audio conversion]",
                    "segments": [],
                    "lang": "auto",
                    "meta": {
                        "filename": filename, 
                        "mime": mime, 
                        "error": "all_methods_failed",
                        "sarvam_realtime_error": result['meta'].get('error'),
                        "sarvam_batch_error": batch_result['meta'].get('error'),
                        "whisper_error": whisper_result['meta'].get('error'),
                        "ffmpeg_error": ffmpeg_result['meta'].get('error')
                    }
                }
            return batch_result
        
        return result
            
    except Exception as e:
        return {
            "text": f"[SARVAM-ASR: Error transcribing {filename}: {str(e)}]",
            "segments": [],
            "lang": "auto",
            "meta": {"filename": filename, "mime": mime, "error": str(e)}
        }

def _transcribe_realtime(file_bytes: bytes, filename: str, mime: str, api_key: str) -> dict:
    """
    Use Sarvam Real-time API for short audio files (< 1MB)
    """
    try:
        # Use the correct Sarvam API endpoint
        url = "https://api.sarvam.ai/v1/speech-to-text"
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        # Use JSON payload with base64 encoded audio for real-time API
        import base64
        
        headers["Content-Type"] = "application/json"
        
        payload = {
            "model": "saarika",
            "language": "auto",
            "response_format": "json",
            "audio": {
                "data": base64.b64encode(file_bytes).decode('utf-8'),
                "format": mime
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            try:
                result = response.json()
                return {
                    "text": result.get("text", ""),
                    "segments": result.get("segments", []),
                    "lang": result.get("language", "auto"),
                    "meta": {
                        "filename": filename, 
                        "mime": mime, 
                        "provider": "sarvam",
                        "model": "saarika",
                        "api_type": "realtime"
                    }
                }
            except Exception as json_error:
                return {
                    "text": f"[SARVAM-ASR: JSON parsing error for {filename}: {str(json_error)}]",
                    "segments": [],
                    "lang": "auto",
                    "meta": {"filename": filename, "mime": mime, "error": "json_parse_error"}
                }
        else:
            error_detail = response.text if hasattr(response, 'text') else "Unknown error"
            return {
                "text": f"[SARVAM-ASR: API error {response.status_code} for {filename}: {error_detail}]",
                "segments": [],
                "lang": "auto",
                "meta": {"filename": filename, "mime": mime, "error": f"api_error_{response.status_code}"}
            }
            
    except Exception as e:
        return {
            "text": f"[SARVAM-ASR: Real-time API error for {filename}: {str(e)}]",
            "segments": [],
            "lang": "auto",
            "meta": {"filename": filename, "mime": mime, "error": str(e)}
        }

def _transcribe_batch(file_bytes: bytes, filename: str, mime: str, api_key: str) -> dict:
    """
    Use Sarvam Batch API for larger audio files (> 1MB)
    """
    try:
        # Use the batch endpoint for large files
        url = "https://api.sarvam.ai/v1/speech-to-text"
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        # For batch API, we need to upload the file
        files = {
            "audio": (filename, file_bytes, mime)
        }
        
        data = {
            "model": "saarika",
            "language": "auto",
            "enable_diarization": "true",  # Enable speaker diarization for batch
            "response_format": "json"
        }
        
        # Increased timeout for large files
        response = requests.post(url, headers=headers, files=files, data=data, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "text": result.get("text", ""),
                "segments": result.get("segments", []),
                "lang": result.get("language", "auto"),
                "meta": {
                    "filename": filename, 
                    "mime": mime, 
                    "provider": "sarvam",
                    "model": "saarika",
                    "api_type": "batch",
                    "diarization": result.get("diarization", {})
                }
            }
        else:
            return {
                "text": f"[SARVAM-ASR: Batch API error {response.status_code} for {filename}]",
                "segments": [],
                "lang": "auto",
                "meta": {"filename": filename, "mime": mime, "error": f"api_error_{response.status_code}"}
            }
            
    except Exception as e:
        return {
            "text": f"[SARVAM-ASR: Batch API error for {filename}: {str(e)}]",
            "segments": [],
            "lang": "auto",
            "meta": {"filename": filename, "mime": mime, "error": str(e)}
        }

def get_supported_formats() -> list:
    """
    Return list of supported audio formats by Sarvam API
    """
    return [
        "mp3", "mpeg", "mpeg3", "x-mpeg-3", "x-mp3",
        "wav", "x-wav", "wave",
        "aac", "x-aac",
        "aiff", "x-aiff",
        "ogg", "opus",
        "flac", "x-flac",
        "mp4", "x-m4a",
        "amr",
        "x-ms-wma",
        "webm",
        "pcm_s16le", "pcm_l16", "pcm_raw"
    ]
