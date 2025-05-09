import os
import logging
from pathlib import Path
from typing import Optional
import yaml
from openai import OpenAI
from dotenv import load_dotenv
from PromptEngine.prompt_template import build_prompt

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

def extract_competency_profile(user_text: str) -> str:
    """
    Extract competency profile from user text using GPT
    
    Args:
        user_text (str): User's interview transcript
    
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
        
        prompt = build_prompt(user_text)
        
        logging.info("Sending request to GPT...")
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
        logging.error(f"Failed to extract competency profile: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        sample_text = "안녕하세요. 저는 20년간 뷰티 업계에서 마케팅과 제품 개발을 했고, 최근에는 1인 창업을 준비하고 있어요. 협업도 잘 하고요!"
        print(extract_competency_profile(sample_text))
    except Exception as e:
        logging.error(f"Program failed: {str(e)}")
        exit(1)
