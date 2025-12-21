'''
In original jobspy , we have added the ouptput format  dictonary, 
so now
x = scrape_jobs(
            ...
            output_format="dict" // this one is added
            ),
'''

from jobspy import scrape_jobs
from logging import create_logger

log = create_logger("JobDescriptonAnalyzer")

'''
Job info is stored in a dict
'''
'''
here we extract job description from dict of jobs , for each jobs respectively
'''
def extract_job_descriptions(self, jobs):
        """
        Extracts minimal job metadata while preserving order.
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



# here we tell llm to see description from dict we get from above and return json or somekind of format that we will use to match gap and rewrite again.
def analyze_jobs(self, jobs):
        """
        jobs: list of job dicts from JobSpy
        returns: list of dicts with job_meta + analysis
        """
        extracted_jobs = self.extract_job_descriptions(jobs)
        analyzed_jobs = []

        for idx, job in enumerate(extracted_jobs):
            description = job["description"]

            if not description:
                log.warning(f"Job {idx} has no description.")
                analyzed_jobs.append({
                    "job_meta": job,
                    "analysis": None
                })
                continue

            try:
                analysis = self._analyze_single_description(description)
            except Exception as e:
                log.error(f"Analysis failed for job {idx}: {e}")
                analysis = None

            analyzed_jobs.append({
                "job_meta": job,
                "analysis": analysis
            })

        return analyzed_jobs
def _analyze_single_description(self, description_text):
        prompt = f"""
        Extract structured information from this job description.
        Return ONLY valid JSON with these fields:

        - required_skills
        - preferred_skills
        - tools
        - seniority_level
        - responsibilities
        - keywords

        Job Description:
        \"\"\"
        {description_text}
        \"\"\"
        """

        return self.llm.query(prompt)

def match_resume_to_job(self, resume_data, job_analysis):
        """
        Compares resume vs job requirements.
        Returns a structured match result.
        """

        if job_analysis is None:
            return None

        resume_skills = set(
            skill.lower()
            for category in resume_data.get("skills", {}).values()
            for skill in category
        )

        required_skills = set(
            skill.lower()
            for skill in job_analysis.get("required_skills", [])
        )

        preferred_skills = set(
            skill.lower()
            for skill in job_analysis.get("preferred_skills", [])
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

'''
works as
for job in analyzed_jobs:
    if job["analysis"] is None:
        continue

    match = analyzer.match_resume_to_job(resume_data, job["analysis"])
    rewrite_resume(resume_data, match)


'''