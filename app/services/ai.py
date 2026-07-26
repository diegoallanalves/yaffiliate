import os
from dotenv import load_dotenv
load_dotenv()
def generate_text(system_instruction,user_prompt):
    key=os.getenv('OPENAI_API_KEY','').strip()
    if not key:return 'AI mode is not configured yet. Add OPENAI_API_KEY to your .env file.'
    try:
        from openai import OpenAI
        c=OpenAI(api_key=key); m=os.getenv('OPENAI_MODEL','gpt-4.1-mini')
        return c.responses.create(model=m,instructions=system_instruction,input=user_prompt).output_text.strip()
    except Exception as e:return f'AI request failed safely: {e}'
