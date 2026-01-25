"""
Utility functions for ResumeAgent.
"""

import logging
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


def setup_logger(name: str = "ResumeAgent", level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger for ResumeAgent modules.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def validate_resume_data(resume_data: Dict[str, Any]) -> bool:
    """
    Validate that resume data has the expected structure.
    
    Args:
        resume_data: Dictionary containing resume data
        
    Returns:
        True if valid, raises ValidationError if not
    """
    if not isinstance(resume_data, dict):
        raise ValueError("resume_data must be a dictionary")
    
    # Check for required top-level keys (at least one should exist)
    expected_keys = ["name", "email", "summary", "skills", "experience", "education"]
    has_content = any(
        resume_data.get(key) for key in expected_keys
    )
    
    if not has_content:
        raise ValueError("resume_data appears to be empty or invalid")
    
    return True


def validate_file_path(file_path: str, must_exist: bool = False, 
                      extension: Optional[str] = None) -> str:
    """
    Validate and normalize a file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether the file must exist
        extension: Expected file extension (e.g., '.pdf', '.docx')
        
    Returns:
        Normalized absolute path
        
    Raises:
        FileNotFoundError: If must_exist is True and file doesn't exist
        ValueError: If extension doesn't match
    """
    if not file_path:
        raise ValueError("file_path cannot be empty")
    
    path = Path(file_path).expanduser().resolve()
    
    if must_exist and not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if extension:
        if not path.suffix.lower() == extension.lower():
            raise ValueError(f"File must have {extension} extension, got {path.suffix}")
    
    return str(path)


def ensure_directory(directory_path: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        Absolute path to directory
    """
    path = Path(directory_path).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    return sanitized


def format_contact_info(contact_data: Dict[str, str]) -> str:
    """
    Format contact information into a readable string.
    
    Args:
        contact_data: Dictionary with name, email, mobile_number
        
    Returns:
        Formatted contact string
    """
    parts = []
    if contact_data.get("name"):
        parts.append(contact_data["name"])
    if contact_data.get("email"):
        parts.append(contact_data["email"])
    if contact_data.get("mobile_number"):
        parts.append(contact_data["mobile_number"])
    
    return " | ".join(parts) if parts else ""


def merge_resume_data(base_resume: Dict[str, Any], 
                     updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge updates into base resume data.
    
    Args:
        base_resume: Base resume data
        updates: Updates to apply
        
    Returns:
        Merged resume data
    """
    merged = base_resume.copy()
    
    for key, value in updates.items():
        if key in merged and isinstance(merged[key], list) and isinstance(value, list):
            # Merge lists
            merged[key] = merged[key] + value
        elif key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            # Merge dictionaries
            merged[key] = {**merged[key], **value}
        else:
            # Overwrite
            merged[key] = value
    
    return merged

