import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "100"))
EMBED_DIM = int(os.getenv("EMBED_DIM", "1024"))

class Settings:
    session_ttl = SESSION_TTL_SECONDS
    max_file_mb = MAX_FILE_MB
    embed_dim = EMBED_DIM

settings = Settings()
