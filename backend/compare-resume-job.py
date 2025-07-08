from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import os

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update if frontend is hosted elsewhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compare-resume-job/")
async def compare_resume_job(
        resume: UploadFile = File(...),
        jobtext: str = Form(None),
        joburl: str = Form(None)
):
    # Validate resume file type
    if not resume.filename.endswith(".pdf"):
        return {"error": "Resume must be a PDF file."}

    # Save resume temporarily
    resume_path = f"temp_{resume.filename}"
    with open(resume_path, "wb") as f:
        f.write(await resume.read())

    # Get job description text
    job_description = ""

    if jobtext:
        job_description = jobtext
    elif joburl:
        try:
            response = requests.get(joburl, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            job_description = soup.get_text(separator="\n")
        except Exception as e:
            os.remove(resume_path)
            return {"error": f"Failed to fetch job description from URL: {str(e)}"}
    else:
        os.remove(resume_path)
        return {"error": "No job description provided."}

    # ---- Do actual comparison logic here ----
    # For now, return dummy response
    result = {
        "match_score": "82%",
        "summary": "Your resume contains most required keywords.",
        "resume_filename": resume.filename,
        "job_description_snippet": job_description[:200]
    }

    os.remove(resume_path)
    return result
