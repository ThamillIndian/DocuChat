def read_text_any(file_bytes: bytes, filename: str, mime: str) -> dict:
    name = filename.lower()
    if name.endswith(".txt") or mime.startswith("text/"):
        txt = file_bytes.decode(errors="ignore")
    elif name.endswith(".pdf"):
        try:
            # Try to extract text from PDF
            import io
            from PyPDF2 import PdfReader
            pdf_stream = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_stream)
            txt = ""
            for page in reader.pages:
                txt += page.extract_text() + "\n"
            if not txt.strip():
                txt = f"[PDF {filename} - no text content found]"
        except ImportError:
            txt = f"[PDF {filename} - PyPDF2 not installed - install with: pip install PyPDF2"
        except Exception as e:
            txt = f"[PDF {filename} extraction failed: {str(e)}"
    elif name.endswith(".docx"):
        txt = f"[DOCX {filename} extracted text placeholder]"
    elif name.endswith((".pptx",".ppt")):
        txt = f"[PPTX {filename} extracted text placeholder]"
    elif name.endswith(".csv"):
        txt = file_bytes.decode(errors="ignore")
    elif name.endswith((".png",".jpg",".jpeg")):
        txt = f"[OCR {filename} placeholder]"
    elif name.endswith((".md", ".markdown")):
        txt = file_bytes.decode(errors="ignore")
    elif name.endswith((".json", ".xml", ".html", ".htm")):
        txt = file_bytes.decode(errors="ignore")
    elif name.endswith((".log", ".py", ".js", ".css", ".sql")):
        txt = file_bytes.decode(errors="ignore")
    else:
        # Try to decode as text for unknown file types
        try:
            txt = file_bytes.decode(errors="ignore")
            if len(txt.strip()) > 0:
                txt = f"[Unknown file type: {filename}]\n{txt}"
            else:
                txt = f"[Binary file: {filename} - {len(file_bytes)} bytes]"
        except:
            txt = f"[Unsupported-doc bytes len={len(file_bytes)}]"
    return {"text": txt, "meta": {"filename": filename, "mime": mime}}
