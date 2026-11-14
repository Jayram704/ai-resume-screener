"""
AI Resume Screener - Elegant UI inspired by clean serif + gold design
"""

import streamlit as st
import httpx

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Elegant Theme CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

/* Background */
.stApp {
    background-color: #f8f5f0;
}

/* Main container */
.main .block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Typography */
h1, .main-title {
    font-family: 'Playfair Display', serif !important;
    font-weight: 600 !important;
    color: #1c1917 !important;
    letter-spacing: -0.02em;
}

.main-title {
    font-size: 2.6rem !important;
    margin-bottom: 0.3rem !important;
}

.subtitle {
    font-family: 'Inter', sans-serif;
    color: #78716c;
    font-size: 1.05rem;
    margin-bottom: 2.2rem;
}

/* Section titles */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 600;
    color: #1c1917;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
}

/* Score box */
.score-box {
    background: linear-gradient(145deg, #8b6914, #a67c2d);
    color: #fafaf9;
    border-radius: 18px;
    padding: 1.8rem 1.5rem;
    text-align: center;
    margin: 1.2rem 0 1.5rem 0;
    box-shadow: 0 4px 12px rgba(139, 105, 20, 0.25);
}
.score-value {
    font-family: 'Playfair Display', serif;
    font-size: 3.4rem;
    font-weight: 700;
    line-height: 1;
}
.score-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    opacity: 0.9;
    margin-top: 0.35rem;
    letter-spacing: 0.03em;
}

/* Skill tags */
.skill-tag {
    display: inline-block;
    background: #f5f0e6;
    color: #5c4a1f;
    border: 1px solid #e0d5b8;
    padding: 0.28rem 0.85rem;
    border-radius: 999px;
    font-size: 0.84rem;
    margin: 0.25rem 0.35rem 0.25rem 0;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}
.skill-tag.missing {
    background: #faf5f5;
    color: #7f1d1d;
    border-color: #e7d3d3;
}

/* Buttons */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.4rem !important;
    border: none !important;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background-color: #a67c2d !important;
    color: #fafaf9 !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #8b6914 !important;
    box-shadow: 0 2px 8px rgba(139, 105, 20, 0.3);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f3efe8;
    border-right: 1px solid #e7e5e4;
}
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    font-family: 'Playfair Display', serif !important;
    color: #1c1917 !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 8px !important;
    border: 1px solid #d6d3d1 !important;
    background: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
}

/* Match history cards */
.match-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.3rem;
    background: #ffffff;
    border-radius: 12px;
    margin-bottom: 0.7rem;
    border: 1px solid #e7e5e4;
}
.match-score {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 600;
}

/* Divider */
hr {
    border-color: #e7e5e4 !important;
    margin: 2rem 0 !important;
}
</style>
""", unsafe_allow_html=True)


def api_get(path: str):
    try:
        r = httpx.get(f"{API_URL}{path}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Could not reach API: {e}")
        return None


def api_post(path: str, **kwargs):
    try:
        r = httpx.post(f"{API_URL}{path}", timeout=30, **kwargs)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# ---------- Header ----------
st.markdown('<h1 class="main-title">AI Resume Screener</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Parse resumes. Match them to roles. Get clear, explainable scores.</p>', unsafe_allow_html=True)


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### Create Job")
    st.caption("Define the role you want to screen against")

    job_title = st.text_input("Job Title", value="Backend Engineer")
    job_skills = st.text_input(
        "Required Skills",
        value="python, fastapi, sql, docker, aws",
        help="Comma-separated"
    )
    job_desc = st.text_area(
        "Job Description",
        height=150,
        value=(
            "We are looking for a Backend Engineer with strong Python skills. "
            "Experience with FastAPI, relational databases, and cloud services is required. "
            "You will design and maintain APIs and work closely with the data team."
        ),
    )

    if st.button("Save Job", type="primary", use_container_width=True):
        payload = {
            "title": job_title,
            "description": job_desc,
            "required_skills": job_skills,
        }
        result = api_post("/jobs", json=payload)
        if result:
            st.success(f"Job saved (ID: {result['id']})")
            st.rerun()


# ---------- Main layout ----------
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="section-title">Upload Resume</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "PDF or DOCX",
        type=["pdf", "docx"],
        label_visibility="collapsed"
    )

    if uploaded:
        st.caption(f"File: **{uploaded.name}**")
        if st.button("Parse & Store Resume", type="primary", use_container_width=True):
            with st.spinner("Extracting text and skills..."):
                files = {"file": (uploaded.name, uploaded.getvalue())}
                result = api_post("/resumes", files=files)
            if result:
                st.success("Resume stored")
                st.markdown(f"**Candidate:** {result['candidate_name']}")
                skills = result.get("extracted_skills", "")
                if skills:
                    tags = "".join(
                        [f'<span class="skill-tag">{s.strip()}</span>' for s in skills.split(",") if s.strip()]
                    )
                    st.markdown(tags, unsafe_allow_html=True)
                st.rerun()


with col_right:
    st.markdown('<div class="section-title">Run Screening</div>', unsafe_allow_html=True)

    jobs = api_get("/jobs") or []
    resumes = api_get("/resumes") or []

    if not jobs or not resumes:
        st.info("Create a job (sidebar) and upload a resume to begin.")
    else:
        job_options = {f"{j['title']}  (#{j['id']})": j["id"] for j in jobs}
        resume_options = {
            f"{r['candidate_name']} — {r['filename']}": r["id"] for r in resumes
        }

        selected_job = st.selectbox("Select Job", list(job_options.keys()))
        selected_resume = st.selectbox("Select Resume", list(resume_options.keys()))

        if st.button("Screen Candidate", type="primary", use_container_width=True):
            payload = {
                "job_id": job_options[selected_job],
                "resume_id": resume_options[selected_resume],
            }
            with st.spinner("Analyzing match..."):
                result = api_post("/screen", json=payload)

            if result:
                score = result["score"]

                st.markdown(f"""
                <div class="score-box">
                    <div class="score-value">{score}</div>
                    <div class="score-label">MATCH SCORE</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**Matched Skills**")
                if result["matched_skills"]:
                    tags = "".join([f'<span class="skill-tag">{s}</span>' for s in result["matched_skills"]])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.caption("None detected")

                st.markdown("**Missing Skills**")
                if result["missing_skills"]:
                    tags = "".join([f'<span class="skill-tag missing">{s}</span>' for s in result["missing_skills"]])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.caption("None — strong coverage")

                st.info(result["summary"])


# ---------- Recent Matches ----------
st.markdown("---")
st.markdown('<div class="section-title">Recent Matches</div>', unsafe_allow_html=True)

matches = api_get("/matches") or []
if matches:
    for m in matches[:7]:
        score = m.get("score", 0)
        if score >= 70:
            color = "#a67c2d"
        elif score >= 50:
            color = "#b45309"
        else:
            color = "#b91c1c"

        st.markdown(f"""
        <div class="match-card">
            <div>
                <strong style="color:#1c1917;">{m.get('candidate_name', 'Unknown')}</strong>
                <span style="color:#a8a29e;"> → </span>
                <strong style="color:#1c1917;">{m.get('job_title', 'Unknown role')}</strong>
                <div style="font-size:0.88rem; color:#78716c; margin-top:0.25rem; font-family:'Inter',sans-serif;">
                    {m.get('summary', '')}
                </div>
            </div>
            <div class="match-score" style="color:{color};">{score}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.caption("No matches yet. Upload a resume and run a screening to see results here.")
