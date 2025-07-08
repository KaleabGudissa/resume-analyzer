import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

export const analyzeResume = (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post(`${API_BASE}/analyze-resume/`, formData);
};

export const compareWithJob = (resumeFile, jobFile) => {
    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('job', jobFile);
    return axios.post(`${API_BASE}/compare-job/`, formData);
};
