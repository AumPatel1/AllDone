"""
BuildResume - Unified interface for building and customizing resumes.
Orchestrates all ResumeAgent modules to provide a complete resume processing workflow.
"""

from typing import Dict, List, Optional, Any
import os
from .ResumeLoader import load_resume
from .JobDecriptionAnalyzer import JobDescriptionAnalyzer
from .RewriteResume import rewrite_resume_data
from .Exporter import build_docx


class BuildResume:
    """
    Main class for building and customizing resumes.
    Provides a unified interface for all resume processing operations.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize BuildResume with an optional LLM client.
        
        Args:
            llm_client: Optional LLM client for job analysis and resume rewriting
        """
        self.llm_client = llm_client
        self.analyzer = JobDescriptionAnalyzer(llm_client=llm_client) if llm_client else None
        self.resume_data = None
    
    def load_resume_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Load resume data from a PDF file.
        
        Args:
            pdf_path: Path to the resume PDF file
            
        Returns:
            Dictionary containing parsed resume data
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF is invalid
        """
        self.resume_data = load_resume(pdf_path)
        return self.resume_data
    
    def analyze_job(self, job_description: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a single job description.
        
        Args:
            job_description: The job description text
            
        Returns:
            Dictionary with structured job analysis or None if analysis fails
        """
        if self.analyzer is None:
            raise ValueError("LLM client is required for job analysis. Initialize BuildResume with llm_client.")
        
        return self.analyzer._analyze_single_description(job_description)
    
    def analyze_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Analyze multiple jobs from a list of job dictionaries.
        
        Args:
            jobs: List of job dictionaries (from jobspy or similar)
            
        Returns:
            List of dictionaries with job_meta + analysis
        """
        if self.analyzer is None:
            raise ValueError("LLM client is required for job analysis. Initialize BuildResume with llm_client.")
        
        return self.analyzer.analyze_jobs(jobs)
    
    def match_resume_to_job(self, job_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Match current resume data to a job analysis.
        
        Args:
            job_analysis: Dictionary containing job analysis results
            
        Returns:
            Dictionary with match results or None if resume not loaded
        """
        if self.resume_data is None:
            raise ValueError("Resume data not loaded. Call load_resume_from_pdf() first.")
        
        if self.analyzer is None:
            raise ValueError("LLM client is required for job matching.")
        
        return self.analyzer.match_resume_to_job(self.resume_data, job_analysis)
    
    def customize_for_job(
        self, 
        job_analysis: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Customize resume for a specific job by rewriting sections.
        
        Args:
            job_analysis: Dictionary containing job analysis results
            output_path: Optional path to save customized resume as DOCX
            
        Returns:
            Dictionary with customized resume data
            
        Raises:
            ValueError: If resume data not loaded
        """
        if self.resume_data is None:
            raise ValueError("Resume data not loaded. Call load_resume_from_pdf() first.")
        
        # Rewrite resume data to match job
        customized_resume = rewrite_resume_data(
            self.resume_data.copy(),
            job_analysis,
            llm_client=self.llm_client
        )
        
        # Save to DOCX if output path provided
        if output_path:
            build_docx(customized_resume, output_path)
        
        return customized_resume
    
    def export_resume(self, output_path: str, resume_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Export resume data to DOCX format.
        
        Args:
            output_path: Path where the DOCX file should be saved
            resume_data: Optional resume data dictionary (uses loaded resume if not provided)
            
        Raises:
            ValueError: If resume data not available
        """
        data_to_export = resume_data or self.resume_data
        
        if data_to_export is None:
            raise ValueError("Resume data not loaded. Call load_resume_from_pdf() first or provide resume_data.")
        
        build_docx(data_to_export, output_path)
    
    def get_resume_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently loaded resume data.
        
        Returns:
            Dictionary containing resume data or None if not loaded
        """
        return self.resume_data


# Example usage:
"""
# Initialize with LLM client
builder = BuildResume(llm_client=your_llm_client)

# Load resume
resume_data = builder.load_resume_from_pdf('resume.pdf')

# Analyze a job
job_analysis = builder.analyze_job(job_description_text)

# Match resume to job
match_results = builder.match_resume_to_job(job_analysis)

# Customize resume for job and export
customized = builder.customize_for_job(job_analysis, output_path='customized_resume.docx')

# Or analyze multiple jobs
jobs = scrape_jobs(search_term="software engineer", output_format="dict")
analyzed_jobs = builder.analyze_jobs(jobs)

for job in analyzed_jobs:
    if job["analysis"]:
        match = builder.match_resume_to_job(job["analysis"])
        if match:
            builder.customize_for_job(job["analysis"], f"resume_{job['job_meta']['company']}.docx")
"""

