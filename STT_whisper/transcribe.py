import whisper
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

def transcribe_and_save(
    audio_path: str,
    save_name: Optional[str] = None,
    model_size: str = "base"
) -> str:
    """
    Transcribe audio file and save the transcript
    
    Args:
        audio_path (str): Path to the audio file
        save_name (str, optional): Name for the transcript file
        model_size (str): Size of the Whisper model to use (tiny, base, small, medium, large)
    
    Returns:
        str: Transcribed text
    """
    try:
        # Load configuration
        config = load_config()
        
        # Set default values
        save_name = save_name or config.get('default_transcript_name', 'transcript1.txt')
        transcript_dir = config['directories']['transcripts']
        
        # Create directory if it doesn't exist
        os.makedirs(transcript_dir, exist_ok=True)
        
        logging.info(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        
        logging.info(f"Transcribing audio file: {audio_path}")
        result = model.transcribe(audio_path)
        transcript_text = result["text"]
        
        # Save transcript
        save_path = os.path.join(transcript_dir, save_name)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)
        
        logging.info(f"Transcript saved to: {save_path}")
        return transcript_text
        
    except Exception as e:
        logging.error(f"Transcription failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        config = load_config()
        audio_path = config.get('default_audio_file', 'sample_audio.wav')
        transcribe_and_save(audio_path, save_name="interview_senior1.txt")
    except Exception as e:
        logging.error(f"Program failed: {str(e)}")
        exit(1)
