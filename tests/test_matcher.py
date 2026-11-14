from app.services.matcher import compute_match_score, skill_overlap


def test_skill_overlap():
    matched, missing = skill_overlap(
        ["python", "fastapi", "docker"],
        ["python", "sql", "docker", "aws"]
    )
    assert "python" in matched
    assert "docker" in matched
    assert "sql" in missing
    assert "aws" in missing


def test_compute_match_score():
    score, matched, missing, summary = compute_match_score(
        resume_text="Experienced Python developer with FastAPI and Docker.",
        job_description="Looking for Python FastAPI engineer. Docker and AWS preferred.",
        resume_skills=["python", "fastapi", "docker"],
        job_skills=["python", "fastapi", "docker", "aws"],
    )
    assert 0 <= score <= 100
    assert "python" in matched
    assert "aws" in missing
    assert "match" in summary.lower()
