"""Resume text extraction and simple, explainable skill detection."""
from __future__ import annotations
import re
from pathlib import Path

KNOWN_SKILLS = [
    "python", "java", "sql", "excel", "statistics", "data visualization", "power bi",
    "machine learning", "scikit-learn", "pandas", "numpy", "git", "llm",
    "prompt engineering", "rag", "embeddings", "api", "data structures",
    "html", "css", "javascript", "react", "networking", "linux",
    "security fundamentals", "siem", "docker", "cloud fundamentals", "ci/cd",
    "testing", "selenium", "nlp", "transformers", "etl", "data modeling",
    "databases", "communication", "requirements analysis", "ui design",
    "ux research", "figma", "prototyping", "research methods", "technical writing",
    "feature engineering", "problem solving",
]

def extract_pdf_text(uploaded_file) -> str:
    """Extract text from a Streamlit UploadedFile using PyMuPDF."""
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is not installed. Run: pip install PyMuPDF") from exc
    data = uploaded_file.getvalue()
    doc = fitz.open(stream=data, filetype="pdf")
    try:
        return "\n".join(page.get_text("text") for page in doc)
    finally:
        doc.close()

def extract_skills(text: str) -> list[str]:
    """Detect known skill phrases with word boundaries; this is a baseline, not perfect NLP."""
    haystack = re.sub(r"\s+", " ", (text or "").lower())
    found = []
    for skill in KNOWN_SKILLS:
        pattern = r"(?<![a-z0-9+#])" + re.escape(skill.lower()) + r"(?![a-z0-9+#])"
        if re.search(pattern, haystack):
            found.append(skill)
    return sorted(set(found))

def read_text_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")
