import os
import logging
from pathlib import Path
from typing import Optional
import yaml
from openai import OpenAI
from dotenv import load_dotenv

# Configure logging
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
            'system_role': "당신은 이력서를 분석하여 핵심 역량을 추출하는 AI입니다.",
            'output_format': [
                "학력: OOO",
                "직업/직무: OOO",
                "근무 기간: OOO",
                "주요 프로젝트 경험: OOO",
                "보유 기술: OOO",
                "강점: OOO",
                "협업 능력: OOO",
                "성격/성향: OOO",
                "최근 관심사: OOO",
                "기대하는 수익: OOO"
            ]
        })
        
        # Build prompt
        prompt = f"""
{template['system_role']}
아래 이력서 내용을 바탕으로 핵심 역량을 다음 형식으로 정리하세요:

[출력 예시]
{chr(10).join(template['output_format'])}

[이력서 내용]
{resume_text}

[정리된 결과]
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
        # Load configuration
        config = load_config()
        
        # Load API key
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Build prompt
        prompt = build_resume_prompt(resume_text)
        
        logging.info("Sending request to GPT for resume analysis...")
        response = client.chat.completions.create(
            model=config.get('gpt_model', 'gpt-4'),
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