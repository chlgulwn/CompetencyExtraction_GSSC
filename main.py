import os
import logging
from pathlib import Path
from typing import Optional
import yaml
from STT_whisper.transcribe import transcribe_and_save
from PromptEngine.extracting_profile import extract_competency_profile
from PromptEngine.resume_analyzer import analyze_resume
from utils.utils_file import load_transcript, save_profile_to_csv

os.environ["PATH"] += os.pathsep + r"C:\Users\hyeju\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin"

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

def run_pipeline(
    input_path: str,
    input_type: str = "audio",
    txt_save_name: Optional[str] = None,
    csv_path: Optional[str] = None
) -> None:
    """
    Run the complete pipeline for processing input and extracting competencies
    
    Args:
        input_path (str): Path to the input file (audio or resume)
        input_type (str): Type of input ("audio" or "resume")
        txt_save_name (str, optional): Name for the transcript file
        csv_path (str, optional): Path for saving the competency profile
    """
    try:
        config = load_config()
        
        txt_save_name = txt_save_name or config.get('default_transcript_name', 'interview1.txt')
        csv_path = csv_path or config.get('default_csv_path', 'interview_data/extracted_profiles.csv')
        
        if input_type == "audio":
            print("Step 1: Transcribing audio...")
            transcribe_and_save(input_path, save_name=txt_save_name)
            
            print("Step 2: Loading transcript...")
            txt_path = os.path.join("interview_data", "transcripts", txt_save_name)
            user_text = load_transcript(txt_path)
            
        elif input_type == "resume":
            print("Step 1: Loading resume...")
            with open(input_path, 'r', encoding='utf-8') as f:
                user_text = f.read()
            
        else:
            raise ValueError(f"Unsupported input type: {input_type}")
        
        print("Step 3: Extracting profile via GPT...")
        profile = extract_competency_profile(user_text)
        print("\nGPT Result:\n", profile)
        
        print("Step 4: Saving result to CSV...")
        save_profile_to_csv(profile, csv_path)
        print("Done! Your result has been saved.")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        config = load_config()
        
        input_type = input("Select your input type (audio/resume): ").lower()
        if input_type not in ["audio", "resume"]:
            raise ValueError("The input type should be 'audio' or 'resume'.")
            
        input_path = input(f"{input_type} Enter the path to the file: ")
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File not found: {input_path}")
            
        run_pipeline(input_path, input_type=input_type)
        
    except Exception as e:
        logging.error(f"Program failed: {str(e)}")
        exit(1)