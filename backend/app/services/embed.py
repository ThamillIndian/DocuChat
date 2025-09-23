import hashlib

def embed_text(s: str) -> list[float]:
    # Stable toy embedding; replace with sentence-transformers later.
    h = hashlib.sha256(s.encode()).digest()
    return [int.from_bytes(h[i:i+4],"big")/2**31 for i in range(0,32,4)]
