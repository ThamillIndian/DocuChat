"""
Fallback ASR service for when SARVAM API is not available
"""
import os
import subprocess
import tempfile
from typing import Dict, Any

def transcribe_with_whisper(file_bytes: bytes, filename: str, mime: str) -> Dict[str, Any]:
    """
    Fallback transcription using OpenAI Whisper Python API
    """
    try:
        # Import whisper
        import whisper
        
        # Save file to temporary location
        with tempfile.NamedTemporaryFile(suffix=f".{filename.split('.')[-1]}", delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name
        
        try:
            # Load whisper model
            model = whisper.load_model("base")
            
            # Transcribe audio
            result = model.transcribe(temp_path)
            
            return {
                "text": result.get("text", ""),
                "segments": result.get("segments", []),
                "lang": result.get("language", "auto"),
                "meta": {
                    "filename": filename, 
                    "mime": mime, 
                    "provider": "whisper",
                    "model": "base"
                }
            }
        
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except ImportError:
        return {
            "text": f"[FALLBACK-ASR: Whisper not installed for {filename}. Please install with: pip install openai-whisper]",
            "segments": [],
            "lang": "auto",
            "meta": {"filename": filename, "mime": mime, "error": "whisper_not_installed"}
        }
    except Exception as e:
        return {
            "text": f"[FALLBACK-ASR: Error with Whisper for {filename}: {str(e)}]",
            "segments": [],
            "lang": "auto",
            "meta": {"filename": filename, "mime": mime, "error": str(e)}
        }

def transcribe_with_ffmpeg_whisper(file_bytes: bytes, filename: str, mime: str) -> Dict[str, Any]:
    """
    Alternative fallback using ffmpeg + whisper
    """
    try:
        # Check if ffmpeg is available
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return {
                "text": f"[FALLBACK-ASR: FFmpeg not available for {filename}]",
                "segments": [],
                "lang": "auto",
                "meta": {"filename": filename, "mime": mime, "error": "ffmpeg_not_available"}
            }
        
        # Save file to temporary location
        with tempfile.NamedTemporaryFile(suffix=f".{filename.split('.')[-1]}", delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name
        
        try:
            # Convert to wav using ffmpeg
            wav_path = temp_path.replace(f".{filename.split('.')[-1]}", ".wav")
            result = subprocess.run([
                'ffmpeg', '-i', temp_path, '-ar', '16000', '-ac', '1', wav_path, '-y'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Read the converted audio
                with open(wav_path, 'rb') as f:
                    wav_data = f.read()
                
                # Try whisper on the converted file
                return transcribe_with_whisper(wav_data, filename.replace('.mp4', '.wav'), 'audio/wav')
            else:
                return {
                    "text": f"[FALLBACK-ASR: FFmpeg conversion failed for {filename}: {result.stderr}]",
                    "segments": [],
                    "lang": "auto",
                    "meta": {"filename": filename, "mime": mime, "error": "ffmpeg_failed"}
                }
        
        finally:
            # Clean up temporary files
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            if os.path.exists(wav_path):
                os.unlink(wav_path)
                
    except Exception as e:
        return {
            "text": f"[FALLBACK-ASR: Error with FFmpeg+Whisper for {filename}: {str(e)}]",
            "segments": [],
            "lang": "auto",
            "meta": {"filename": filename, "mime": mime, "error": str(e)}
        }
