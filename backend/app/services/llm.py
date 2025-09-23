import time
import os
from typing import Generator

def answer_stream(prompt: str) -> Generator[str, None, None]:
    """
    Stream responses from Gemini 2.5 Flash model
    """
    try:
        from google import genai
        
        # Initialize Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            yield "Error: GEMINI_API_KEY not found in environment variables"
            return
            
        client = genai.Client(api_key=api_key)
        
        # Generate content (Gemini doesn't support streaming in this SDK version)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # Stream response in clean, readable chunks
        if hasattr(response, 'text') and response.text:
            text = response.text.strip()
            
            # Clean up citations to be more readable
            import re
            # Replace [#1:4] with [Source 1]
            text = re.sub(r'\[#(\d+):\d+(?:-\d+)?\]', r'[Source \1]', text)
            
            # Split into paragraphs for better streaming
            paragraphs = text.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Stream paragraph word by word for smooth typing effect
                    words = paragraph.strip().split()
                    for word in words:
                        yield word + " "
                        time.sleep(0.03)  # Faster typing speed
                    yield "\n\n"  # Add paragraph break
                    time.sleep(0.1)  # Pause between paragraphs
                
    except ImportError:
        # Fallback to stub if google-genai not installed
        yield "Error: google-genai package not installed. Install with: pip install google-genai"
        yield "Falling back to stub response..."
        txt = f"[STUB] {prompt[:200]}"
        for tok in txt.split():
            yield tok + " "
            time.sleep(0.003)
            
    except Exception as e:
        yield f"Error calling Gemini API: {str(e)}"
        yield "Falling back to stub response..."
        txt = f"[STUB] {prompt[:200]}"
        for tok in txt.split():
            yield tok + " "
            time.sleep(0.003)
