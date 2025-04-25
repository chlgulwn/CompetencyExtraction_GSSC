import os
import logging
from pathlib import Path
from typing import Optional
import yaml

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

def build_prompt(user_text: str) -> str:
    """
    Build the prompt for competency extraction
    
    Args:
        user_text (str): User's interview transcript
    
    Returns:
        str: Formatted prompt
    """
    try:
        # Load configuration
        config = load_config()
        
        # Get template from config or use default
        template = config.get('prompt_template', {
            'system_role': "당신은 시니어의 경험과 특기를 정리해주는 인터뷰 AI입니다.",
            'output_format': [
                "학력: OOO",
                "직업/직무: OOO",
                "근무 기간: OOO",
                "뷰티 프로젝트 경험: OOO",
                "후회되는 점: OOO",
                "강점: OOO",
                "협업 능력: OOO",
                "성격/성향: OOO",
                "최근 관심사: OOO",
                "투자 가능 자원 (돈/시간): OOO",
                "기대하는 수익: OOO"
            ]
        })
        
        # Build prompt
        prompt = f"""
{template['system_role']}
아래 사용자의 대화 내용을 바탕으로 핵심 역량을 다음 형식으로 정리하세요:

[출력 예시]
{chr(10).join(template['output_format'])}

[사용자 응답]
{user_text}

[정리된 결과]
"""
        return prompt
        
    except Exception as e:
        logging.error(f"Failed to build prompt: {str(e)}")
        raise
