def chunk_text(text: str, size: int = 800):
    words = text.split()
    out, buf = [], []
    for w in words:
        buf.append(w)
        if len(" ".join(buf)) > size:
            out.append(" ".join(buf)); buf=[]
    if buf: out.append(" ".join(buf))
    return out or [text]
