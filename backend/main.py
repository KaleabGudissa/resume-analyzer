# backend/main.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import fitz  # PyMuPDF
import requests, re, asyncio, concurrent.futures, logging
from bs4 import BeautifulSoup
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------------------------
# FastAPI setup
# --------------------------------------------------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # change to your frontend URL in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("resume-analyzer")
logger.setLevel(logging.INFO)

# --------------------------------------------------------------------
# Configuration constants
# --------------------------------------------------------------------
MAX_PDF_PAGES       = 10      # parse only first N pages
MAX_TFIDF_FEATURES  = 5000    # cap TF-IDF vocab size
MIN_JOB_DESC_WORDS  = 30      # reject < 30-word descriptions
TOKEN_RE            = re.compile(r"\b\w+\b", re.IGNORECASE)
THREAD_POOL         = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# --------------------------------------------------------------------
# Utility helpers
# --------------------------------------------------------------------
def extract_text_from_pdf(data: bytes, max_pages: int = MAX_PDF_PAGES) -> str:
    """Return plain text from the first *max_pages* of a PDF (no hang)."""
    doc = fitz.open(stream=data, filetype="pdf")
    pages = min(max_pages, doc.page_count)
    return "\n".join(doc.load_page(i).get_text() for i in range(pages))

def extract_text_from_url(url: str) -> Optional[str]:
    """Fetch <p> text from a job-posting web page."""
    try:
        r = requests.get(url, timeout=10,
                         headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            logger.warning("URL returned %s", r.status_code)
            return None
        soup = BeautifulSoup(r.content, "html.parser")
        return " ".join(p.get_text(" ", strip=True) for p in soup.find_all("p"))
    except Exception as exc:
        logger.warning("URL fetch failed: %s", exc)
        return None

def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())

async def async_cosine(a: str, b: str) -> float:
    """Compute cosine similarity in a thread (prevents event-loop block)."""
    loop = asyncio.get_running_loop()
    def _calc() -> float:
        try:
            vec = TfidfVectorizer(stop_words="english",
                                  max_features=MAX_TFIDF_FEATURES)
            tfidf = vec.fit_transform([a, b])
            return float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
        except ValueError:            # not enough terms
            return 0.0
    return await loop.run_in_executor(THREAD_POOL, _calc)

# --------------------------------------------------------------------
# /analyze-resume
# --------------------------------------------------------------------
@app.post("/analyze-resume/")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        text = extract_text_from_pdf(await resume.read())
        words = tokenize(text)
        word_count = len(words)
        top_words  = Counter(words).most_common(10)

        keyword_bank = ["python", "java", "sql", "react",
                        "leadership", "communication",
                        "problem", "teamwork"]
        found = [kw for kw in keyword_bank if kw in words]
        resume_score = min(100, len(found)*10 + (10 if word_count > 300 else 0))

        return {
            "status": "success",
            "data": {
                "word_count": word_count,
                "top_words": top_words,
                "found_keywords": found,
                "resume_score": resume_score,
            },
            "summary": f"Length {word_count} words · "
                       f"keywords {len(found)} · score {resume_score}/100",
        }

    except Exception as exc:
        logger.exception("Analyze failed")
        return {"status": "error",
                "message": f"Resume analysis failed: {exc}"}

# --------------------------------------------------------------------
# /compare-resume-job
# --------------------------------------------------------------------
@app.post("/compare-resume-job/")
async def compare_resume_job(
        resume: UploadFile = File(...),
        jobtext: Optional[str] = Form(None),
        joburl: Optional[str] = Form(None),
):
    try:
        resume_txt = extract_text_from_pdf(await resume.read())

        # obtain job description
        if jobtext:
            job_desc = jobtext
        elif joburl:
            job_desc = extract_text_from_url(joburl)
            if not job_desc:
                return {"status": "error",
                        "message": "Could not fetch job description from URL."}
        else:
            return {"status": "error",
                    "message": "Provide jobtext or joburl."}

        # sanity-check length
        if len(tokenize(job_desc)) < MIN_JOB_DESC_WORDS:
            return {"status": "error",
                    "message": "Job description too short for reliable comparison."}

        # keyword overlap
        resume_tokens = set(tokenize(resume_txt))
        job_tokens    = set(tokenize(job_desc))
        matched = sorted(resume_tokens & job_tokens)
        missing = sorted(job_tokens - resume_tokens)
        kw_pct  = round(len(matched)/len(job_tokens)*100, 2)

        # cosine similarity as overall similarity
        similarity_pct = round((await async_cosine(resume_txt, job_desc))*100, 2)
        verdict = ("Excellent" if similarity_pct >= 80
                   else "Good" if similarity_pct >= 60
        else "Fair – improve alignment")

        return {
            "status": "success",
            "data": {
                "similarity_percentage": similarity_pct,
                "keyword_match_percentage": kw_pct,
                "matched_keywords": matched[:20],
                "missing_keywords": missing[:20],
            },
            "summary": f"Similarity {similarity_pct}% ({verdict}); "
                       f"keyword match {kw_pct}%",
        }

    except Exception as exc:
        logger.exception("Comparison failed")
        return {"status": "error",
                "message": f"Comparison failed: {exc}"}
