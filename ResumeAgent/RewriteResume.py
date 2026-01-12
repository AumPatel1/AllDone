"""
Resume rewriting module.
Rewrites resume sections to better match job requirements using LLM.
"""

from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path for potential imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def summary_prompt(summary: str, job_analysis: Dict[str, Any]) -> str:
    """
    Creates a prompt for rewriting the resume summary.
    
    Args:
        summary: Original resume summary
        job_analysis: Job analysis dictionary with keywords and skills
        
    Returns:
        Formatted prompt string
    """
    keywords = job_analysis.get("keywords", [])
    required_skills = job_analysis.get("required_skills", [])
    
    keywords_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
    skills_str = ", ".join(required_skills) if isinstance(required_skills, list) else str(required_skills)
    
    return f"""
Rewrite this resume summary to better match the job.
DO NOT fabricate experience. Only emphasize relevant existing experience.

Original summary:
{summary}

Job keywords:
{keywords_str}

Required skills:
{skills_str}

Return only the rewritten summary, no additional text.
"""


def bullet_prompt(bullet: str, job_analysis: Dict[str, Any]) -> str:
    """
    Creates a prompt for rewriting a resume bullet point.
    
    Args:
        bullet: Original bullet point text
        job_analysis: Job analysis dictionary with keywords
        
    Returns:
        Formatted prompt string
    """
    keywords = job_analysis.get("keywords", [])
    keywords_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
    
    return f"""
Rewrite this resume bullet to better align with the job.
Preserve truth. Do not exaggerate. Only rephrase to emphasize relevance.

Bullet:
{bullet}

Job keywords:
{keywords_str}

Return only the rewritten bullet point, no additional text.
"""


def rewrite_text(prompt: str, llm_client=None) -> str:
    """
    Rewrites text using an LLM client.
    
    Args:
        prompt: The prompt to send to the LLM
        llm_client: LLM client object with a query() method
        
    Returns:
        Rewritten text or original prompt if LLM is not available
    """
    if llm_client is None:
        # Fallback: return a placeholder or the original text
        print("Warning: No LLM client provided. Cannot rewrite text.")
        return prompt
    
    try:
        response = llm_client.query(prompt)
        if isinstance(response, str):
            return response.strip()
        return str(response).strip()
    except Exception as e:
        print(f"Error rewriting text: {e}")
        return prompt  # Return original on error


def rewrite_resume_data(
    resume_data: Dict[str, Any], 
    job_analysis: Dict[str, Any],
    llm_client=None
) -> Dict[str, Any]:
    """
    Rewrites resume data to better match job requirements.
    
    Args:
        resume_data: Dictionary containing resume information
        job_analysis: Dictionary containing job analysis results
        llm_client: Optional LLM client for rewriting
        
    Returns:
        Dictionary with rewritten resume sections
    """
    if not isinstance(resume_data, dict):
        raise ValueError("resume_data must be a dictionary")
    
    if not isinstance(job_analysis, dict):
        raise ValueError("job_analysis must be a dictionary")
    
    rewritten = resume_data.copy()

    # Rewrite summary if it exists
    if "summary" in rewritten and rewritten["summary"]:
        summary_text = rewritten["summary"]
        if isinstance(summary_text, list):
            summary_text = " ".join(summary_text)
        
        try:
            rewritten["summary"] = rewrite_text(
                summary_prompt(str(summary_text), job_analysis),
                llm_client
            )
        except Exception as e:
            print(f"Error rewriting summary: {e}")
            # Keep original summary on error

    # Rewrite experience bullets if experience exists
    if "experience" in rewritten and rewritten["experience"]:
        rewritten_experience = []
        experience_list = rewritten["experience"]
        
        # Handle both list of strings and list of dicts
        if isinstance(experience_list, list) and len(experience_list) > 0:
            if isinstance(experience_list[0], dict):
                # Experience is a list of role dictionaries
                for role in experience_list:
                    new_role = role.copy()
                    bullets = role.get("bullets", [])
                    
                    if isinstance(bullets, list):
                        new_bullets = []
                        for bullet in bullets:
                            try:
                                rewritten_bullet = rewrite_text(
                                    bullet_prompt(str(bullet), job_analysis),
                                    llm_client
                                )
                                new_bullets.append(rewritten_bullet)
                            except Exception as e:
                                print(f"Error rewriting bullet: {e}")
                                new_bullets.append(bullet)  # Keep original on error
                        
                        new_role["bullets"] = new_bullets
                    else:
                        # Single bullet as string
                        try:
                            new_role["bullets"] = [rewrite_text(
                                bullet_prompt(str(bullets), job_analysis),
                                llm_client
                            )]
                        except Exception as e:
                            print(f"Error rewriting experience: {e}")
                    
                    rewritten_experience.append(new_role)
            else:
                # Experience is a list of strings
                rewritten_experience = []
                for exp_item in experience_list:
                    try:
                        rewritten_item = rewrite_text(
                            bullet_prompt(str(exp_item), job_analysis),
                            llm_client
                        )
                        rewritten_experience.append(rewritten_item)
                    except Exception as e:
                        print(f"Error rewriting experience item: {e}")
                        rewritten_experience.append(exp_item)
        
        rewritten["experience"] = rewritten_experience

    return rewritten
