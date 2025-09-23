def _score(q: str, t: str, vq: list[float], vt: list[float]) -> float:
    swq, swt = set(q.lower().split()), set(t.lower().split())
    j = len(swq & swt) / max(1, len(swq | swt))
    dot = sum(a*b for a,b in zip(vq, vt))
    return j*0.4 + dot*0.6

from .embed import embed_text

def top_k(query: str, session, k=8):
    vq = embed_text(query)
    cands = []
    for ch in session.chunks:
        vt = session.embeddings[ch["id"]]
        cands.append((_score(query, ch["text"], vq, vt), ch))
    cands.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in cands[:k]]
