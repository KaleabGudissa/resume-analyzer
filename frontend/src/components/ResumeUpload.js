import React, { useState } from 'react';
import axios from 'axios';
import './ResumeUpload.css';

export default function ResumeUpload() {
    const [resume, setResume] = useState(null);
    const [jobText, setJobText] = useState('');
    const [jobUrl, setJobUrl] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleResumeChange = (e) => {
        setResume(e.target.files[0]);
        setResult(null);
    };

    const handleAnalyze = async () => {
        if (!resume) return alert('Please upload your resume.');

        const formData = new FormData();
        formData.append('resume', resume);

        setLoading(true);
        try {
            const res = await axios.post('http://127.0.0.1:8000/analyze-resume/', formData);
            setResult(res.data);
        } catch (err) {
            alert('Failed to analyze resume');
            console.error(err);
        }
        setLoading(false);
    };

    const handleCompare = async () => {
        if (!resume) return alert('Please upload your resume.');
        if (!jobText.trim() && !jobUrl.trim()) {
            return alert('Please paste job description text or provide a URL.');
        }

        const formData = new FormData();
        formData.append('resume', resume);
        if (jobText.trim()) formData.append('jobtext', jobText);
        if (jobUrl.trim()) formData.append('joburl', jobUrl);

        setLoading(true);
        try {
            const res = await axios.post('http://127.0.0.1:8000/compare-resume-job/', formData);
            setResult(res.data);
        } catch (err) {
            alert('Comparison failed');
            console.error(err);
        }
        setLoading(false);
    };

    // Helper: render summary badge when available
    const SummaryBadge = ({ summary }) => (
        <div className="badge">{summary}</div>
    );

    // Helper: render similarity bar when similarity_percentage exists
    const SimilarityBar = ({ percent }) => (
        <div className="bar-wrap">
            <div className="bar-fill" style={{ width: `${percent}%` }} />
            <span className="bar-label">{percent}% overall similarity</span>
        </div>
    );

    return (
        <div className="resume-container">
            <h1 className="resume-title">AI Resume Analyzer</h1>

            <label className="resume-label">Upload Resume (PDF)</label>
            <input type="file" accept=".pdf" onChange={handleResumeChange} />

            <div className="resume-buttons">
                <button className="resume-button" onClick={handleAnalyze}>
                    Analyze Resume
                </button>
            </div>

            <label className="resume-label">Paste Job Description (optional)</label>
            <textarea
                rows={5}
                placeholder="Paste job description text here..."
                value={jobText}
                onChange={(e) => setJobText(e.target.value)}
            />

            <label className="resume-label">Or Enter Job Posting URL (optional)</label>
            <input
                type="text"
                placeholder="https://company.com/job123"
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
            />

            <div className="resume-buttons">
                <button className="resume-button" onClick={handleCompare}>
                    Compare with Job Description
                </button>
            </div>

            {loading && <p className="resume-loading">⏳ Processing...</p>}

            {result && result.status === 'success' && (
                <div className="resume-result">
                    {result.summary && <SummaryBadge summary={result.summary} />}

                    {result.data?.similarity_percentage !== undefined && (
                        <SimilarityBar percent={result.data.similarity_percentage} />
                    )}

                    <h3>Raw Response</h3>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}

            {result && result.status === 'error' && (
                <div className="resume-error">{result.message}</div>
            )}
        </div>
    );
}