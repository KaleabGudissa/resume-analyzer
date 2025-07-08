# AI-Powered Resume Analyzer 🔍

**Live demo:** <https://resume-analyzer0.netlify.app/>  

Need to know—quickly—whether a résumé actually matches a job post?  
Upload a PDF, paste (or link) the job description, and get a clear “fit score,” keyword overlap, and plain-English feedback in seconds.

> “It feels like having a mini recruiter on my laptop.” — me, after writing too many cover letters

---

## What it does

* **Reads your résumé** (first 10 pages, no freezes) and counts words, skills, top terms.
* **Pulls the job ad** (paste text *or* drop a URL) and cleans it up automatically.
* **Compares them** with TF-IDF cosine similarity *and* a straight keyword hit-list.
* Flags red flags—missing keywords, generic objectives, unexplained gaps (basic regex).
* Gives you a one-line verdict: **Excellent / Good / Fair**.

---

## What I used

| Layer      | Tech |
|------------|------|
| **Backend** | FastAPI • PyMuPDF • scikit-learn • BeautifulSoup • Uvicorn |
| **Frontend** | React 18 • Axios • jsPDF (download report) |
| **Hosting** | Render (API) • Netlify (static SPA) |
| **Language** | Python 3.11 • Node 18 |

---

## Run it locally

```bash
git clone https://github.com/KaleabGudissa/resume-analyzer.git
cd resume-analyzer

# --- backend ---
cd backend
python -m venv venv && venv\Scripts\activate     # Win  (for macOS: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload                        # http://127.0.0.1:8000

# --- frontend ---
cd ../frontend
npm install
npm start                                        # http://localhost:3000
