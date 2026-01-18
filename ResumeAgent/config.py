"""
Configuration constants and settings for ResumeAgent.
"""

import os
from typing import List, Dict

# Default section names for resume parsing
DEFAULT_SECTIONS = {
    "summary": ["summary", "professional summary", "objective", "profile", "about"],
    "skills": ["skills", "technical skills", "core competencies", "competencies", "expertise"],
    "experience": ["experience", "work experience", "employment", "work history", "professional experience"],
    "projects": ["projects", "project experience", "key projects", "notable projects"],
    "education": ["education", "academic background", "qualifications", "academic qualifications"]
}

# Phone number patterns for contact extraction
PHONE_PATTERNS = [
    r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
    r'\+?\d{10,15}',  # Generic international
    r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',  # (123) 456-7890
]

# Email pattern
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Default file paths
DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Resumes")

# Export settings
DOCX_SETTINGS = {
    "font_name": "Calibri",
    "font_size": 11,
    "heading_font_size": {
        1: 16,  # Name
        2: 14,  # Section headings
        3: 12   # Subsection headings
    }
}

# LLM settings
LLM_DEFAULTS = {
    "max_tokens": 300,
    "temperature": 0.7,
    "model": "gpt-3.5-turbo"  # Default model
}

# Job analysis fields
JOB_ANALYSIS_FIELDS = [
    "required_skills",
    "preferred_skills",
    "tools",
    "seniority_level",
    "responsibilities",
    "keywords"
]

# Resume data structure template
RESUME_TEMPLATE = {
    "name": "",
    "email": "",
    "mobile_number": "",
    "summary": [],
    "skills": [],
    "experience": [],
    "projects": [],
    "education": []
}

