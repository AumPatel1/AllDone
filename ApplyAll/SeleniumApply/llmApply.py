'''
Will be making multi llm system that person can choose to have
'''

import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key= os.getenv('OPENAI_API_KEY')

def generate_llm_response(question,job_desc,user_data):
   prompt = f"Based on resume: {user_data['experience']} and skills: {user_data['skills']}. Job: {job_desc}. Answer: {question} in 200 words or less."
   response = openai.ChatCompletion.create(
        model  = "gpt-3.5-turbo" #for now
        messages = [{"role":"user","content":"prompt"}]
   )
   return response.choices[0].message['content'].strip()
   