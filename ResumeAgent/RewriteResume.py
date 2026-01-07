
from llm_client import rewrite_text
from prompts import summary_prompt, bullet_prompt

def rewrite_resume_data(resume_data: dict, job_analysis: dict) -> dict:
    rewritten = resume_data.copy()

    
    rewritten["summary"] = rewrite_text(
        summary_prompt(resume_data["summary"], job_analysis)
    )


    rewritten_experience = []

    for role in resume_data["experience"]:
        new_role = role.copy()
        new_bullets = []

        for bullet in role["bullets"]:
            new_bullets.append(
                rewrite_text(bullet_prompt(bullet, job_analysis))
            )

        new_role["bullets"] = new_bullets
        rewritten_experience.append(new_role)

    rewritten["experience"] = rewritten_experience

    return rewritten
