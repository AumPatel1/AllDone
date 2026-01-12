"""
Resume loader module for extracting and parsing resume data from PDF files.
Handles text extraction, section parsing, and basic contact information extraction.
"""

import re
import os
from typing import Dict, List, Optional
from pypdf import PdfReader
from pypdf.errors import PdfReadError


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        PdfReadError: If the PDF cannot be read
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Resume not found: {pdf_path}")
    
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError(f"File must be a PDF: {pdf_path}")

    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) == 0:
            raise ValueError(f"PDF file appears to be empty: {pdf_path}")
        
        full_text = ""
        for page in reader.pages:
            try:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            except Exception as e:
                print(f"Warning: Could not extract text from a page: {e}")
                continue

        if not full_text.strip():
            raise ValueError(f"No text could be extracted from PDF: {pdf_path}")
        
        return full_text
    except PdfReadError as e:
        raise PdfReadError(f"Error reading PDF file {pdf_path}: {e}")


def extract_contact_info(resume_text: str) -> Dict[str, str]:
    """
    Extracts basic contact information from resume text.
    
    Args:
        resume_text: Full resume text
        
    Returns:
        Dictionary with name, email, and mobile_number
    """
    contact_info = {
        "name": "",
        "email": "",
        "mobile_number": ""
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, resume_text)
    if emails:
        contact_info["email"] = emails[0]
    
    # Extract phone number (various formats)
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'\+?\d{10,15}',  # Generic international
        r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',  # (123) 456-7890
    ]
    for pattern in phone_patterns:
        phones = re.findall(pattern, resume_text)
        if phones:
            contact_info["mobile_number"] = phones[0].strip()
            break
    
    # Extract name (first line or before email)
    lines = resume_text.splitlines()
    if lines:
        # Try first non-empty line as name
        for line in lines[:5]:  # Check first 5 lines
            line_clean = line.strip()
            if line_clean and len(line_clean.split()) <= 4:
                # Likely a name if it's short and doesn't contain common section keywords
                if not any(keyword in line_clean.lower() for keyword in 
                          ['summary', 'experience', 'education', 'skills', 'projects', '@']):
                    contact_info["name"] = line_clean
                    break
    
    return contact_info


def split_into_sections(resume_text: str) -> Dict[str, str]:
    """
    Splits resume text into sections based on section headers.
    
    Args:
        resume_text: Full resume text
        
    Returns:
        Dictionary with section names as keys and content as values
    """
    sections = {
        "summary": "",
        "skills": "",
        "experience": "",
        "projects": "",
        "education": ""
    }

    # Expanded section header patterns
    section_patterns = {
        "summary": ["summary", "professional summary", "objective", "profile", "about"],
        "skills": ["skills", "technical skills", "core competencies", "competencies", "expertise"],
        "experience": ["experience", "work experience", "employment", "work history", "professional experience"],
        "projects": ["projects", "project experience", "key projects", "notable projects"],
        "education": ["education", "academic background", "qualifications", "academic qualifications"]
    }

    current_section = None
    lines = resume_text.splitlines()

    for line in lines:
        line_clean = line.strip().lower()
        
        # Check if this line is a section header
        found_section = None
        for section_name, patterns in section_patterns.items():
            if any(pattern in line_clean for pattern in patterns):
                # Additional check: section headers are usually short and may be followed by separator
                if len(line.strip()) < 50:  # Reasonable header length
                    found_section = section_name
                    break
        
        if found_section:
            current_section = found_section
            continue

        # Add content to current section
        if current_section:
            sections[current_section] += line + "\n"

    return sections


def normalize_sections(sections: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Normalizes section content by cleaning and splitting into list items.
    
    Args:
        sections: Dictionary with section names and raw text content
        
    Returns:
        Dictionary with section names and lists of cleaned items
    """
    normalized = {}

    for key, value in sections.items():
        lines = []
        for line in value.splitlines():
            cleaned = line.strip("•- *").strip()
            if cleaned:
                lines.append(cleaned)
        
        normalized[key] = lines

    return normalized


def load_resume(pdf_path: str) -> Dict[str, any]:
    """
    Main function to load and parse a resume PDF.
    
    Args:
        pdf_path: Path to the resume PDF file
        
    Returns:
        Dictionary containing parsed resume data with contact info and sections
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If PDF is invalid or empty
        PdfReadError: If PDF cannot be read
    """
    try:
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # Extract contact information
        contact_info = extract_contact_info(extracted_text)
        
        # Split into sections
        split_sections = split_into_sections(extracted_text)
        
        # Normalize sections
        normalized_sections = normalize_sections(split_sections)
        
        # Combine contact info and sections
        resume_data = {
            **contact_info,
            **normalized_sections
        }
        
        return resume_data
        
    except Exception as e:
        raise RuntimeError(f"Failed to load resume from {pdf_path}: {e}") from e