import whisper
import numpy as np
import sounddevice as sd
import queue
import threading
import logging
from pathlib import Path
from typing import Optional, Callable
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

class RealtimeTranscriber:
    def __init__(
        self,
        model_size: str = "base",
        sample_rate: int = 16000,
        channels: int = 1,
        callback: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize real-time transcriber
        
        Args:
            model_size (str): Size of the Whisper model
            sample_rate (int): Audio sample rate
            channels (int): Number of audio channels
            callback (Callable): Function to call when new transcription is available
        """
        self.model = whisper.load_model(model_size)
        self.sample_rate = sample_rate
        self.channels = channels
        self.callback = callback
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.transcription_thread = None
        
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio input"""
        if status:
            logging.warning(f"Audio input status: {status}")
        self.audio_queue.put(indata.copy())
        
    def process_audio(self):
        """Process audio data and generate transcriptions"""
        while self.is_recording:
            try:
                # Get audio data from queue
                audio_data = self.audio_queue.get(timeout=1.0)
                
                # Convert to float32 and normalize
                audio_data = audio_data.astype(np.float32) / 32768.0
                
                # Transcribe
                result = self.model.transcribe(
                    audio_data,
                    language="ko",
                    fp16=False
                )
                
                # Call callback if transcription is available
                if result["text"].strip() and self.callback:
                    self.callback(result["text"].strip())
                    
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error processing audio: {str(e)}")
                continue
                
    def start_recording(self):
        """Start recording and transcription"""
        if self.is_recording:
            return
            
        self.is_recording = True
        
        # Start audio stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self.audio_callback
        )
        self.stream.start()
        
        # Start transcription thread
        self.transcription_thread = threading.Thread(target=self.process_audio)
        self.transcription_thread.start()
        
        logging.info("Started recording and transcription")
        
    def stop_recording(self):
        """Stop recording and transcription"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        # Stop audio stream
        self.stream.stop()
        self.stream.close()
        
        # Wait for transcription thread to finish
        if self.transcription_thread:
            self.transcription_thread.join()
            
        logging.info("Stopped recording and transcription") 