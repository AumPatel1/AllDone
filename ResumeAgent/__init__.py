"""
ResumeAgent - A comprehensive resume processing and customization toolkit.

This package provides tools for:
- Loading and parsing resume data from PDFs
- Analyzing job descriptions
- Matching resumes to job requirements
- Rewriting resumes to better match job descriptions
- Exporting resumes to various formats (DOCX, etc.)
"""

from .ResumeLoader import load_resume, extract_text_from_pdf, extract_contact_info
from .JobDecriptionAnalyzer import JobDescriptionAnalyzer
from .RewriteResume import rewrite_resume_data, rewrite_text, summary_prompt, bullet_prompt
from .Exporter import build_docx
from .BuildResume import BuildResume

__all__ = [
    'BuildResume',
    'load_resume',
    'extract_text_from_pdf',
    'extract_contact_info',
    'JobDescriptionAnalyzer',
    'rewrite_resume_data',
    'rewrite_text',
    'summary_prompt',
    'bullet_prompt',
    'build_docx',
]

__version__ = '1.0.0'

