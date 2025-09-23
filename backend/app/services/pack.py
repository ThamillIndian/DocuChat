def pack_context(chunks: list[dict], budget_chars=6000) -> str:
    out, used = [], 0
    for i, ch in enumerate(chunks):
        # Clean format with source reference
        seg = f"\n[Source {i+1}]\n{ch['text']}\n"
        if used + len(seg) > budget_chars: break
        out.append(seg); used += len(seg)
    return "".join(out)
