'''
Will be making multi llm system that person can choose to have
'''

import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client with API key
if openai_api_key:
    openai.api_key = openai_api_key


def generate_llm_response(question, job_desc, user_data):
    """
    Generates an LLM response to a job application question.
    
    Args:
        question: The question to answer
        job_desc: Job description text
        user_data: Dictionary containing user experience and skills
        
    Returns:
        Generated answer string
    """
    experience = user_data.get('experience', [])
    skills = user_data.get('skills', [])
    
    # Format experience and skills as strings
    exp_str = '\n'.join(experience) if isinstance(experience, list) else str(experience)
    skills_str = ', '.join(skills) if isinstance(skills, list) else str(skills)
    
    prompt = (
        f"Based on resume experience: {exp_str} "
        f"and skills: {skills_str}. "
        f"Job description: {job_desc}. "
        f"Answer the following question: {question} "
        f"in 200 words or less. Be professional and relevant."
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating LLM response: {e}")
        return f"I have experience in {skills_str} and relevant work background. {question}"
   