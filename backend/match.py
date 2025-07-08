import re

def extract_words(text):
    return set(re.findall(r'\b[a-zA-Z]{4,}\b', text.lower()))

def compare_resume_with_job(resume_text, job_text):
    resume_words = extract_words(resume_text)
    job_words = extract_words(job_text)

    matched = sorted(list(resume_words & job_words))
    missing = sorted(list(job_words - resume_words))
    percent = round((len(matched) / len(job_words)) * 100, 2) if job_words else 0

    feedback = "Good match!" if percent > 70 else "Add more keywords from job posting."

    return {
        "match_percent": percent,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "feedback": feedback
    }
