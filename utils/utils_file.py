import os
import logging
import pandas as pd
from pathlib import Path
from typing import Optional
import yaml
from datetime import datetime

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

def load_transcript(file_path: str) -> str:
    """
    Load transcript from file
    
    Args:
        file_path (str): Path to the transcript file
    
    Returns:
        str: Transcript text
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Failed to load transcript: {str(e)}")
        raise

def save_profile_to_csv(profile: str, csv_path: str) -> None:
    """
    Save competency profile to CSV file
    
    Args:
        profile (str): Extracted competency profile
        csv_path (str): Path to save the CSV file
    """
    try:
        # Load configuration
        config = load_config()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        # Parse profile into dictionary
        profile_dict = {}
        for line in profile.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                profile_dict[key.strip()] = value.strip()
        
        # Add timestamp
        profile_dict['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert to DataFrame
        df = pd.DataFrame([profile_dict])
        
        # Check if file exists
        if os.path.exists(csv_path):
            # Append to existing file
            existing_df = pd.read_csv(csv_path)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        # Save to CSV
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logging.info(f"Profile saved to: {csv_path}")
        
    except Exception as e:
        logging.error(f"Failed to save profile: {str(e)}")
        raise
