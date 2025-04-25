import os
import logging
from pathlib import Path
from typing import Optional
import yaml

from STT_whisper.transcribe import transcribe_and_save
from PromptEngine.extracting_profile import extract_competency_profile
from utils.utils_file import load_transcript, save_profile_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)

def load_config() -> dict:
    """Load configuration from YAML file"""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError("config.yaml file not found")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def validate_audio_file(audio_path: str) -> bool:
    """Validate audio file"""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    valid_extensions = ['.wav', '.mp3', '.m4a']
    if not any(audio_path.lower().endswith(ext) for ext in valid_extensions):
        raise ValueError(f"Invalid audio file format. Supported formats: {', '.join(valid_extensions)}")
    
    return True

def run_pipeline(
    audio_path: str,
    txt_save_name: Optional[str] = None,
    csv_path: Optional[str] = None
) -> None:
    """
    Run the complete pipeline for processing interview audio and extracting competencies
    
    Args:
        audio_path (str): Path to the audio file
        txt_save_name (str, optional): Name for the transcript file
        csv_path (str, optional): Path for saving the competency profile
    """
    try:
        # Load configuration
        config = load_config()
        
        # Set default values if not provided
        txt_save_name = txt_save_name or config.get('default_transcript_name', 'interview1.txt')
        csv_path = csv_path or config.get('default_csv_path', 'interview_data/extracted_profiles.csv')
        
        # Validate input
        validate_audio_file(audio_path)
        
        logging.info("Step 1: Transcribing audio...")
        transcribe_and_save(audio_path, save_name=txt_save_name)
        
        logging.info("Step 2: Loading transcript...")
        txt_path = os.path.join("interview_data", "transcripts", txt_save_name)
        if not os.path.exists(txt_path):
            raise FileNotFoundError(f"Transcript file not found: {txt_path}")
            
        user_text = load_transcript(txt_path)
        
        logging.info("Step 3: Extracting profile via GPT...")
        profile = extract_competency_profile(user_text)
        logging.info(f"\nGPT 결과:\n{profile}")
        
        logging.info("Step 4: Saving result to CSV...")
        save_profile_to_csv(profile, csv_path)
        logging.info("완료! 결과가 저장되었습니다.")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        config = load_config()
        audio_file = config.get('default_audio_file', 'sample_audio.wav')
        run_pipeline(audio_file)
    except Exception as e:
        logging.error(f"Program failed: {str(e)}")
        exit(1)