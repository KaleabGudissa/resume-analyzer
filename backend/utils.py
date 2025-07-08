import os
from datetime import datetime

def validate_file_type(filename, allowed_exts):
    if not any(filename.endswith(ext) for ext in allowed_exts):
        raise ValueError(f"Invalid file type: must be one of {allowed_exts}")

def get_file_metadata(file):
    return {
        "filename": file.filename,
        "size_kb": round(len(file.file.read()) / 1024, 2),
        "upload_time": datetime.utcnow().isoformat()
    }
