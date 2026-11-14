"""
Resume text extraction.

Supports PDF and DOCX. Nothing fancy — just get clean text out.
"""

import io
import re
from typing import Tuple

import pdfplumber
from docx import Document


COMMON_SKILLS = {
    # Programming
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "html", "css", "react", "node.js", "nodejs", "django", "flask",
    "fastapi", "spring", "aws", "azure", "gcp", "docker", "kubernetes",
    "git", "linux", "bash",
    # Data / ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
    "pandas", "numpy", "spark", "hadoop", "nlp", "computer vision",
    # Soft / other
    "agile", "scrum", "jira", "communication", "leadership", "problem solving"
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])


def extract_text(filename: str, file_bytes: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        # fallback: treat as plain text
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return ""


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills(text: str) -> list[str]:
    """Very simple skill extractor based on a keyword list.
    Good enough for a demo, not production-grade NER.
    """
    text_lower = text.lower()
    found = set()
    for skill in COMMON_SKILLS:
        # simple word boundary-ish matching
        if re.search(rf"\b{re.escape(skill)}\b", text_lower):
            found.add(skill)
    return sorted(found)


def guess_candidate_name(text: str) -> str:
    """Naive heuristic: first non-empty line that looks like a name."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return "Unknown"
    # Take first line if it's short
    first = lines[0]
    if len(first.split()) <= 4 and len(first) < 50:
        return first
    return "Unknown"


def parse_resume(filename: str, file_bytes: bytes) -> Tuple[str, str, list[str]]:
    raw = extract_text(filename, file_bytes)
    cleaned = clean_text(raw)
    name = guess_candidate_name(raw)
    skills = extract_skills(cleaned)
    return cleaned, name, skills
