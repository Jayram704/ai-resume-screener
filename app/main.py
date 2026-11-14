from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import engine, get_db, Base
from . import models, schemas
from .services.parser import parse_resume
from .services.matcher import compute_match_score

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Screener",
    description="Parse resumes, match them against job descriptions, and get explainable scores.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "AI Resume Screener API",
        "docs": "/docs",
        "version": "0.1.0",
    }


# ---------- Jobs ----------

@app.post("/jobs", response_model=schemas.JobOut)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    db_job = models.Job(
        title=job.title,
        description=job.description,
        required_skills=job.required_skills or "",
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@app.get("/jobs", response_model=List[schemas.JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).order_by(models.Job.created_at.desc()).all()


@app.get("/jobs/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ---------- Resumes ----------

@app.post("/resumes", response_model=schemas.ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()
    if len(content) > 8 * 1024 * 1024:  # 8 MB limit
        raise HTTPException(status_code=400, detail="File too large (max 8MB)")

    text, name, skills = parse_resume(file.filename, content)

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    db_resume = models.Resume(
        candidate_name=name,
        filename=file.filename,
        raw_text=text,
        extracted_skills=", ".join(skills),
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume


@app.get("/resumes", response_model=List[schemas.ResumeOut])
def list_resumes(db: Session = Depends(get_db)):
    return db.query(models.Resume).order_by(models.Resume.created_at.desc()).all()


@app.get("/resumes/{resume_id}", response_model=schemas.ResumeOut)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


# ---------- Screening ----------

@app.post("/screen", response_model=schemas.ScreenResponse)
def screen_resume(req: schemas.ScreenRequest, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == req.job_id).first()
    resume = db.query(models.Resume).filter(models.Resume.id == req.resume_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job_skills = [s.strip() for s in job.required_skills.split(",") if s.strip()]
    resume_skills = [s.strip() for s in resume.extracted_skills.split(",") if s.strip()]

    score, matched, missing, summary = compute_match_score(
        resume_text=resume.raw_text,
        job_description=job.description,
        resume_skills=resume_skills,
        job_skills=job_skills,
    )

    # Persist the result
    result = models.MatchResult(
        job_id=job.id,
        resume_id=resume.id,
        score=score,
        matched_skills=", ".join(matched),
        missing_skills=", ".join(missing),
        summary=summary,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return schemas.ScreenResponse(
        score=score,
        matched_skills=matched,
        missing_skills=missing,
        summary=summary,
        resume_id=resume.id,
        job_id=job.id,
    )


@app.get("/matches", response_model=List[schemas.MatchResultOut])
def list_matches(db: Session = Depends(get_db)):
    results = (
        db.query(models.MatchResult)
        .order_by(models.MatchResult.created_at.desc())
        .limit(50)
        .all()
    )
    # Enrich a bit for the frontend
    out = []
    for r in results:
        item = schemas.MatchResultOut.model_validate(r)
        item.job_title = r.job.title if r.job else None
        item.candidate_name = r.resume.candidate_name if r.resume else None
        out.append(item)
    return out
