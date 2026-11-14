"""
Resume ↔ Job matching logic.

Currently uses TF-IDF + cosine similarity on the combined text.
Also does simple skill set intersection for explainability.
"""

from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def skill_overlap(resume_skills: List[str], job_skills: List[str]) -> Tuple[List[str], List[str]]:
    resume_set = {s.lower().strip() for s in resume_skills if s}
    job_set = {s.lower().strip() for s in job_skills if s}

    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)
    return matched, missing


def compute_match_score(
    resume_text: str,
    job_description: str,
    resume_skills: List[str],
    job_skills: List[str],
) -> Tuple[float, List[str], List[str], str]:
    """
    Returns:
        score (0-100),
        matched_skills,
        missing_skills,
        short summary
    """
    matched, missing = skill_overlap(resume_skills, job_skills)

    # Semantic-ish score using TF-IDF
    documents = [resume_text or " ", job_description or " "]
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf = vectorizer.fit_transform(documents)
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    except Exception:
        sim = 0.0

    # Blend skill coverage with text similarity
    skill_score = 0.0
    if job_skills:
        skill_score = len(matched) / max(len(job_skills), 1)
    else:
        skill_score = 0.5  # neutral if no skills listed

    # Weighted final score
    final = (0.55 * sim + 0.45 * skill_score) * 100
    final = max(0.0, min(100.0, final))

    # Simple summary
    if final >= 75:
        verdict = "Strong match"
    elif final >= 55:
        verdict = "Moderate match"
    else:
        verdict = "Weak match"

    summary = (
        f"{verdict}. "
        f"Matched {len(matched)} skill(s). "
        f"Missing {len(missing)} required skill(s)."
    )

    return round(final, 1), matched, missing, summary
