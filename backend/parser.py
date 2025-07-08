from io import BytesIO
import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_bytes):
    text = ""
    with fitz.open("pdf", BytesIO(pdf_bytes)) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_resume_sections(text):
    sections = {
        "contact_info": extract_contact_info(text),
        "education": extract_section(text, "education"),
        "experience": extract_section(text, "experience"),
        "skills": extract_section(text, "skills"),
    }
    return sections

def extract_contact_info(text):
    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.search(r'(\(?\d{3}\)?[\s\-]?\d{3}[\-]?\d{4})', text)
    return {
        "email": email.group() if email else "Not found",
        "phone": phone.group() if phone else "Not found"
    }

def extract_section(text, section_name):
    pattern = rf"{section_name}[\s\S]{{0,500}}"  # 500 chars from section title
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group().strip() if match else "Section not found"
