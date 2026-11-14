# AI Resume Screener

A small full-stack application that parses resumes (PDF/DOCX), extracts skills, and scores them against job descriptions.

Built to practice a few things I care about:
- Clean API design with FastAPI
- Basic document preprocessing
- Simple model-style scoring (TF-IDF + skill overlap)
- Proper database schema with SQLAlchemy
- A usable frontend for demos

This is **not** a production ATS. It’s a learning / portfolio project that actually works end-to-end.

## Features

- Upload PDF or DOCX resumes
- Create job postings with required skills
- Automatic skill extraction (keyword-based)
- Match score (0–100) with matched / missing skills
- Results stored in SQLite
- Streamlit UI for quick demos
- Full OpenAPI docs at `/docs`

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Parsing**: pdfplumber + python-docx
- **Matching**: scikit-learn TF-IDF + cosine similarity + skill set overlap
- **Frontend**: Streamlit
- **API docs**: automatic via FastAPI

## Quick Start

```bash
# 1. Create virtualenv (recommended)
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

# 2. Install
pip install -r requirements.txt

# 3. Start the API
uvicorn app.main:app --reload --port 8000

# 4. In another terminal, start the UI
streamlit run frontend/streamlit_app.py
```

Then open:
- API docs → http://localhost:8000/docs
- UI → http://localhost:8501

## API Overview

| Method | Endpoint       | Description                  |
|--------|----------------|------------------------------|
| POST   | /jobs          | Create a job                 |
| GET    | /jobs          | List jobs                    |
| POST   | /resumes       | Upload & parse a resume      |
| GET    | /resumes       | List resumes                 |
| POST   | /screen        | Score a resume against a job |
| GET    | /matches       | Recent screening results     |

## Project Structure

```
app/
  main.py           # FastAPI routes
  models.py         # SQLAlchemy models
  schemas.py        # Pydantic schemas
  database.py
  services/
    parser.py       # PDF/DOCX → text + skills
    matcher.py      # scoring logic
frontend/
  streamlit_app.py
```

## Design Notes

- Skill extraction is intentionally simple (keyword list). Real systems use NER + embeddings.
- Matching blends text similarity with skill coverage so the score is somewhat explainable.
- Database keeps full history of jobs, resumes, and match results.
- SQLite keeps the project zero-config. Easy to swap for Postgres later.

## Possible Improvements

- Replace TF-IDF with sentence-transformers for better semantic matching
- Better name / contact extraction
- Support for multiple job applications per candidate
- Auth + multi-tenancy
- Export shortlist as CSV

## License

MIT
