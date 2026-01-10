"""
Resume extraction module.
Can use pyresparser if available, otherwise falls back to basic extraction.
"""

import sys
import os

try:
    from pyresparser import ResumeParser
    USE_PYRESPARSER = True
except ImportError:
    USE_PYRESPARSER = False
    # Add project root to path for ResumeLoader import
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from ResumeAgent.ResumeLoader import load_resume


def extract_resume_data(resume_path):
    """
    Extracts data from a resume PDF.
    
    Args:
        resume_path: Path to the resume PDF file
        
    Returns:
        Dictionary containing extracted resume data (name, email, experience, skills, etc.)
    """
    if USE_PYRESPARSER:
        try:
            data = ResumeParser(resume_path).get_extracted_data()
            return data
        except Exception as e:
            print(f"Error using pyresparser: {e}. Falling back to basic extraction.")
            return _extract_basic_data(resume_path)
    else:
        # Use the existing ResumeLoader from the project
        return _extract_basic_data(resume_path)


def _extract_basic_data(resume_path):
    """
    Basic resume extraction using the project's ResumeLoader.
    Converts the loaded sections to a format compatible with the application code.
    """
    try:
        sections = load_resume(resume_path)
        # Convert to expected format
        return {
            'name': '',  # Would need additional extraction
            'email': '',  # Would need additional extraction
            'mobile_number': '',  # Would need additional extraction
            'experience': sections.get('experience', []),
            'skills': sections.get('skills', []),
            'summary': sections.get('summary', []),
            'education': sections.get('education', []),
            'projects': sections.get('projects', [])
        }
    except Exception as e:
        print(f"Error extracting resume data: {e}")
        return {
            'name': '',
            'email': '',
            'mobile_number': '',
            'experience': [],
            'skills': [],
            'summary': [],
            'education': [],
            'projects': []
        }