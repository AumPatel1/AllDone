'''
It is assumed everything is clear in pdf format and sections are well defined.
We still have to  extract other infomation and have to add execptions and error handling.
'''



from pypdf import PdfReader
import os

def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Resume not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    full_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    return full_text

def split_into_sections(resume_text):
    sections = {
        "summary": "",
        "skills": "",
        "experience": "",
        "projects": "",
        "education": ""
    }

    current_section = None

    for line in resume_text.splitlines():
        line_clean = line.strip().lower()

        if line_clean in ["summary", "professional summary"]:
            current_section = "summary"
            continue
        elif line_clean in ["skills", "technical skills"]:
            current_section = "skills"
            continue
        elif line_clean in ["experience", "work experience"]:
            current_section = "experience"
            continue
        elif line_clean in ["projects"]:
            current_section = "projects"
            continue
        elif line_clean in ["education"]:
            current_section = "education"
            continue

        if current_section:
            sections[current_section] += line + "\n"

    return sections

def final_sections(sections):
    normalized = {}

    for key, value in sections.items():
        lines = [
            line.strip("•- ").strip()
            for line in value.splitlines()
            if line.strip()
        ]
        normalized[key] = lines

    return normalized

def load_resume(pdf_path):
    extracted_text = extract_text_from_pdf(pdf_path)
    split_sections = split_into_sections(extracted_text)
    final_sections = final_sections(split_sections)
    return final_sections