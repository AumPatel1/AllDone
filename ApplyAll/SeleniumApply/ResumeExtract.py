from pyresparser import ResumePasrser

def extract_resume_data(resume_path):
    data = ResumeParser(resume_path).get_extracted_data()
    return data