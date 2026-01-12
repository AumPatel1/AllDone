"""
Job Description Analyzer module.
Analyzes job descriptions using LLM to extract structured information
and matches them against resume data.

In original jobspy, we have added the output format dictionary,
so now:
x = scrape_jobs(
    ...
    output_format="dict"  # this one is added
)
"""

import json
import re
from typing import List, Dict, Optional, Any
from jobspy import scrape_jobs
from jobspy.util import create_logger

log = create_logger("JobDescriptionAnalyzer")


class JobDescriptionAnalyzer:
    """
    Analyzes job descriptions and matches them against resume data.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize the analyzer with an LLM client.
        
        Args:
            llm_client: LLM client object with a query() method
        """
        self.llm = llm_client
        if llm_client is None:
            log.warning("No LLM client provided. Analysis will not work without one.")
    
    def extract_job_descriptions(self, jobs: List[Dict]) -> List[Dict]:
        """
        Extracts minimal job metadata while preserving order.
        
        Args:
            jobs: List of job dictionaries from JobSpy
            
        Returns:
            List of dictionaries with title, company, description, and url
        """
        extracted = []

        for job in jobs:
            extracted.append({
                "title": job.get("title"),
                "company": job.get("company"),
                "description": job.get("description"),
                "url": job.get("job_url")
            })

        return extracted

    def analyze_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Analyzes a list of jobs and extracts structured information.
        
        Args:
            jobs: List of job dicts from JobSpy
            
        Returns:
            List of dicts with job_meta + analysis
        """
        if self.llm is None:
            log.error("Cannot analyze jobs: No LLM client provided")
            return []
        
        extracted_jobs = self.extract_job_descriptions(jobs)
        analyzed_jobs = []

        for idx, job in enumerate(extracted_jobs):
            description = job.get("description")

            if not description:
                log.warning(f"Job {idx} ({job.get('title', 'Unknown')}) has no description.")
                analyzed_jobs.append({
                    "job_meta": job,
                    "analysis": None
                })
                continue

            try:
                analysis = self._analyze_single_description(description)
            except Exception as e:
                log.error(f"Analysis failed for job {idx} ({job.get('title', 'Unknown')}): {e}")
                analysis = None

            analyzed_jobs.append({
                "job_meta": job,
                "analysis": analysis
            })

        return analyzed_jobs
    
    def _analyze_single_description(self, description_text: str) -> Optional[Dict[str, Any]]:
        """
        Analyzes a single job description using LLM.
        
        Args:
            description_text: The job description text
            
        Returns:
            Dictionary with structured analysis or None if analysis fails
        """
        if not description_text or not description_text.strip():
            return None
        
        prompt = f"""
Extract structured information from this job description.
Return ONLY valid JSON with these fields:

- required_skills: list of required technical skills
- preferred_skills: list of preferred/nice-to-have skills
- tools: list of tools/technologies mentioned
- seniority_level: string (e.g., "entry", "mid", "senior", "lead")
- responsibilities: list of key responsibilities
- keywords: list of important keywords from the job description

Job Description:
\"\"\"
{description_text}
\"\"\"

Return ONLY the JSON object, no additional text.
"""
        
        try:
            response = self.llm.query(prompt)
            
            # Try to extract JSON from response
            if isinstance(response, dict):
                return response
            
            # If response is a string, try to parse JSON
            if isinstance(response, str):
                # Try to find JSON in the response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                # If no match, try parsing the whole response
                return json.loads(response)
            
            log.warning(f"Unexpected response type from LLM: {type(response)}")
            return None
            
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse JSON from LLM response: {e}")
            return None
        except Exception as e:
            log.error(f"Error analyzing job description: {e}")
            return None

    def match_resume_to_job(self, resume_data: Dict, job_analysis: Optional[Dict]) -> Optional[Dict]:
        """
        Compares resume vs job requirements.
        Returns a structured match result.
        
        Args:
            resume_data: Dictionary containing resume information
            job_analysis: Dictionary containing job analysis results
            
        Returns:
            Dictionary with match results or None if analysis is None
        """
        if job_analysis is None:
            return None

        # Handle different resume skill formats
        resume_skills = set()
        skills_data = resume_data.get("skills", [])
        
        if isinstance(skills_data, list):
            # If skills is a list of strings
            resume_skills = {skill.lower().strip() for skill in skills_data if skill}
        elif isinstance(skills_data, dict):
            # If skills is a dict with categories
            resume_skills = {
                skill.lower().strip()
                for category in skills_data.values()
                for skill in (category if isinstance(category, list) else [category])
                if skill
            }

        required_skills = set(
            skill.lower().strip()
            for skill in job_analysis.get("required_skills", [])
            if skill
        )

        preferred_skills = set(
            skill.lower().strip()
            for skill in job_analysis.get("preferred_skills", [])
            if skill
        )

        matched_required = resume_skills & required_skills
        missing_required = required_skills - resume_skills
        matched_preferred = resume_skills & preferred_skills

        return {
            "matched_required_skills": list(matched_required),
            "missing_required_skills": list(missing_required),
            "matched_preferred_skills": list(matched_preferred),
            "emphasize_skills": list(matched_required | matched_preferred),
            "resume_gaps": list(missing_required),
            "safe_to_add": [],  # always empty → no fabrication
        }


# Example usage:
# analyzer = JobDescriptionAnalyzer(llm_client=your_llm_client)
# jobs = scrape_jobs(search_term="software engineer", output_format="dict")
# analyzed_jobs = analyzer.analyze_jobs(jobs)
# 
# for job in analyzed_jobs:
#     if job["analysis"] is None:
#         continue
#     match = analyzer.match_resume_to_job(resume_data, job["analysis"])
#     # Use match to rewrite resume