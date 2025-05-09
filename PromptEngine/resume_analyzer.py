import os
import logging
from pathlib import Path
from typing import Optional
import yaml
from openai import OpenAI
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config() -> dict:
    """Load configuration from YAML file"""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError("config.yaml file not found")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def build_resume_prompt(resume_text: str) -> str:
    """
    Build prompt for resume analysis
    
    Args:
        resume_text (str): Text content of the resume
    
    Returns:
        str: Formatted prompt
    """
    try:
        # Load configuration
        config = load_config()
        
        # Get template from config or use default
        template = config.get('resume_prompt_template', {
            'system_role': "You are an AI that analyzes resumes and extracts key skills.",
            'output_format': [
                "Education: OOO",
                "Job Title/Role: OOO",
                "Employment Period: OOO",
                "Key Project Experiences: OOO",
                "Skills: OOO",
                "Strengths: OOO",
                "Collaboration Skills: OOO",
                "Personality Traits: OOO",
                "Recent Interests: OOO",
                "Expected Salary: OOO"
            ]
        })
        
        # Build prompt
        prompt = f"""
{template['system_role']}
Based on the resume content below, summarize the key skills in the following format in English:

[Example Output]
{chr(10).join(template['output_format'])}

[Resume Content]
{resume_text}

[Summarized Results]
"""
        return prompt
        
    except Exception as e:
        logging.error(f"Failed to build resume prompt: {str(e)}")
        raise

def analyze_resume(resume_text: str) -> str:
    """
    Analyze resume and extract competencies
    
    Args:
        resume_text (str): Text content of the resume
    
    Returns:
        str: Extracted competency profile
    """
    try:
        config = load_config()
        
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        client = OpenAI(api_key=api_key)
        
        prompt = build_resume_prompt(resume_text)
        
        logging.info("Sending request to GPT for resume analysis...")
        response = client.chat.completions.create(
            model=config.get('gpt_model', 'gpt-4o-mini'),
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        result = response.choices[0].message.content.strip()
        logging.info("Successfully received response from GPT")
        return result
        
    except Exception as e:
        logging.error(f"Failed to analyze resume: {str(e)}")
        raise 