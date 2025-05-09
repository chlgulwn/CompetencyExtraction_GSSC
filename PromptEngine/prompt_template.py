import os
import logging
from pathlib import Path
from typing import Optional
import yaml

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

def build_prompt(user_text: str) -> str:
    """
    Build the prompt for competency extraction
    
    Args:
        user_text (str): User's interview transcript
    
    Returns:
        str: Formatted prompt
    """
    try:
        config = load_config()
        
        template = config.get('prompt_template', {
            'system_role': "You are an interview AI that summarizes the experiences and strengths of seniors.",
            'output_format': [
                "Education: OOO",
                "Job Title/Role: OOO",
                "Employment Period: OOO",
                "Key Project Experiences: OOO",
                "Strengths: OOO",
                "Collaboration Skills: OOO",
                "Personality Traits: OOO",
                "Recent Interests: OOO",
                "Available Resources for Investment (Money/Time): OOO",
                "Expected Returns: OOO"
            ]
        })
        
        prompt = f"""
{template['system_role']}
Based on the user's response below, summarize the key skills in the following format in English:

[Example Output]
{chr(10).join(template['output_format'])}

[User Response]
{user_text}

[Summarized Results]
"""
        return prompt
        
    except Exception as e:
        logging.error(f"Failed to build prompt: {str(e)}")
        raise
