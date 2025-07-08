// src/components/ResumeUpload.js
import React, { useState } from "react";
import axios from "axios";
import { jsPDF } from "jspdf";
import "./ResumeUpload.css";

const API_BASE = process.env.REACT_APP_API || "http://127.0.0.1:8000";

export default function ResumeUpload() {
    // ---------------- state ----------------
    const [resume, setResume] = useState(null);
    const [jobText, setJobText] = useState("");
    const [jobUrl, setJobUrl] = useState("");
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    // -------------- helpers ---------------
    const handleResume = (e) => {
        setResume(e.target.files[0]);
        setResult(null);
    };

    const handleAnalyze = async () => {
        if (!resume || !resume.name.endsWith(".pdf")) {
            alert("Please upload a PDF resume.");
            return;
        }
        const form = new FormData();
        form.append("resume", resume);
        await callEndpoint("/analyze-resume/", form);
    };

    const handleCompare = async () => {
        if (!resume) {
            alert("Upload your resume first.");
            return;
        }
        if (!jobText.trim() && !jobUrl.trim()) {
            alert("Paste a job description or provide a job URL.");
            return;
        }
        const form = new FormData();
        form.append("resume", resume);
        if (jobText.trim()) form.append("jobtext", jobText);
        if (jobUrl.trim()) form.append("joburl", jobUrl);
        await callEndpoint("/compare-resume-job/", form);
    };

    const callEndpoint = async (path, formData) => {
        try {
            setLoading(true);
            const res = await axios.post(`${API_BASE}${path}`, formData);
            setResult(res.data);
        } catch (err) {
            console.error(err);
            alert("Request failed – see console.");
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = () => {
        if (!result || result.status !== "success") {
            alert("Run an analysis first.");
            return;
        }
        const doc = new jsPDF();
        doc.setFontSize(14).text("AI Resume Analyzer – Report", 10, 15);
        doc.setFontSize(11);
        doc.text(`Summary: ${result.summary}`, 10, 30);
        if (result.data?.similarity_percentage !== undefined) {
            doc.text(`Similarity: ${result.data.similarity_percentage}%`, 10, 40);
            doc.text(
                `Keyword match: ${result.data.keyword_match_percentage}%`,
                10,
                48
            );
        }
        const matched = result.data?.matched_keywords || [];
        doc.text("Matched keywords:", 10, 60);
        matched.slice(0, 15).forEach((kw, i) =>
            doc.text(`• ${kw}`, 15, 68 + i * 6)
        );
        doc.save("resume_analysis_report.pdf");
    };

    // --------------- UI -----------------
    return (
        <div className="resume-container">
            <h1 className="resume-title">AI Resume Analyzer</h1>

            {/* resume upload */}
            <label className="resume-label">Upload Resume (PDF)</label>
            <input type="file" accept=".pdf" onChange={handleResume} />

            {/* buttons */}
            <div className="resume-buttons">
                <button className="resume-button" onClick={handleAnalyze}>
                    Analyze Resume
                </button>
            </div>

            {/* job inputs */}
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

            {/* result */}
            {result && (
                <>
                    {result.status === "success" ? (
                        <div className="resume-result">
                            <h3>Result</h3>
                            <p>
                                <strong>{result.summary}</strong>
                            </p>
                            <pre>{JSON.stringify(result.data, null, 2)}</pre>
                        </div>
                    ) : (
                        <div className="resume-result">
                            <h3 style={{ color: "red" }}>Error</h3>
                            <p>{result.message}</p>
                        </div>
                    )}

                    <button className="resume-button" onClick={handleDownload}>
                        Download PDF Report
                    </button>
                </>
            )}
        </div>
    );
}
