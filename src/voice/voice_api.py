"""
Voice API Integration for The Finisher.

This module provides a robust, scalable interface for processing audio files via an external
voice API, designed for enterprise-grade performance and seamless integration with creative workflows.
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ValidationError
import yaml
from datetime import datetime
from retry import retry
from pathlib import Path

# Configure logging for monitoring and analytics, critical for operational insights
logging.basicConfig(
    filename='voice_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load configuration from environment variables or YAML for secure and flexible deployment
CONFIG_FILE = os.getenv('VOICE_API_CONFIG', 'voice_api_config.yaml')
try:
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f) or {}
except FileNotFoundError:
    config = {}
    logging.warning("Configuration file not found, using environment variables")

# Constants for API settings, configurable via YAML or environment
API_KEY = config.get('API_KEY', os.getenv('VOICE_API_KEY', 'your_api_key_here'))
API_URL = config.get('API_URL', os.getenv('VOICE_API_URL', 'https://api.voiceprocessor.com/process'))
TIMEOUT = config.get('TIMEOUT', int(os.getenv('TIMEOUT', 30)))
MAX_RETRIES = config.get('MAX_RETRIES', int(os.getenv('MAX_RETRIES', 3)))
RETRY_DELAY = config.get('RETRY_DELAY', int(os.getenv('RETRY_DELAY', 2)))
SUPPORTED_FORMATS = config.get('SUPPORTED_FORMATS', ['mp3', 'wav', 'ogg', 'flac'])
MAX_FILE_SIZE_BYTES = config.get('MAX_FILE_SIZE_BYTES', 50 * 1024 * 1024)  # 50MB default

# Pydantic model for audio processing configuration validation
class AudioProcessingConfig(BaseModel):
    audio_path: str = Field(..., min_length=1)
    output_format: str = Field(default='json', pattern='^(json|binary)$')
    processing_options: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class VoiceAPIClient:
    """Client for interacting with the voice API, optimized for reliability and scalability."""
    
    def __init__(self, api_url: str = API_URL, api_key: str = API_KEY):
        """
        Initialize the Voice API client with secure configuration.
        
        Args:
            api_url (str): URL of the voice API.
            api_key (str): API key for authentication.
        """
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.session = requests.Session()  # Reuse connections for performance
        logging.info("VoiceAPIClient initialized with URL: %s", self.api_url)

    def validate_audio_file(self, audio_path: str) -> bool:
        """
        Validate audio file for format and size constraints.
        
        Args:
            audio_path (str): Path to the audio file.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            path = Path(audio_path)
            if not path.exists():
                logging.error(f"Audio file not found: {audio_path}")
                return False
            if path.suffix[1:].lower() not in SUPPORTED_FORMATS:
                logging.error(f"Unsupported file format for {audio_path}. Supported: {SUPPORTED_FORMATS}")
                return False
            if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                logging.error(f"File {audio_path} exceeds size limit ({MAX_FILE_SIZE_BYTES} bytes)")
                return False
            logging.info(f"Validated audio file: {audio_path}")
            return True
        except Exception as e:
            logging.error(f"Validation failed for {audio_path}: {e}")
            return False

    @retry(requests.RequestException, tries=MAX_RETRIES, delay=RETRY_DELAY, backoff=2)
    def send_audio_for_processing(self, config: Dict[str, Any]) -> Optional[Dict]:
        """
        Send an audio file to the voice API with retry logic for reliability.
        
        Args:
            config (Dict[str, Any]): Configuration for audio processing.
            
        Returns:
            Optional[Dict]: API response if successful, None otherwise.
        """
        try:
            # Validate configuration
            processing_config = AudioProcessingConfig(**config)
            audio_path = processing_config.audio_path
            
            # Validate audio file
            if not self.validate_audio_file(audio_path):
                return None
            
            # Prepare metadata
            processing_config.metadata.update({
                "processed_at": datetime.utcnow().isoformat(),
                "file_size": os.path.getsize(audio_path)
            })
            
            # Send request
            with open(audio_path, "rb") as audio_file:
                files = {"audio": audio_file}
                data = {
                    "options": json.dumps(processing_config.processing_options),
                    "metadata": json.dumps(processing_config.metadata)
                }
                response = self.session.post(
                    self.api_url,
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=TIMEOUT
                )
                response.raise_for_status()
                
                result = response.json() if processing_config.output_format == 'json' else response.content
                logging.info(f"Successfully processed audio: {audio_path}")
                return result
        except ValidationError as e:
            logging.error(f"Invalid configuration: {e}")
            return None
        except requests.RequestException as e:
            logging.error(f"API request failed for {audio_path}: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error processing {audio_path}: {e}")
            return None

    def process_batch_audio(self, configs: List[Dict[str, Any]]) -> List[Dict]:
        """
        Process multiple audio files in a batch, optimizing for high-volume workflows.
        
        Args:
            configs (List[Dict[str, Any]]): List of audio processing configurations.
            
        Returns:
            List[Dict]: List of results for each audio file.
        """
        results = []
        for config in configs:
            result = self.send_audio_for_processing(config)
            results.append({
                "audio_path": config.get("audio_path", "unknown"),
                "status": "success" if result else "failed",
                "response": result
            })
        logging.info(f"Batch processing completed: {len(results)} files processed")
        return results

    def close(self):
        """Close the session to free resources, ensuring efficient resource management."""
        self.session.close()
        logging.info("VoiceAPIClient session closed")

def main() -> None:
    """Main function demonstrating voice API integration capabilities."""
    client = VoiceAPIClient()
    
    # Sample configurations for demonstration
    sample_configs = [
        {
            "audio_path": "audio/sample1.mp3",
            "output_format": "json",
            "processing_options": {"enhance": True, "noise_reduction": True},
            "metadata": {"track_name": "Sample Track 1"}
        },
        {
            "audio_path": "audio/sample2.wav",
            "output_format": "json",
            "processing_options": {"enhance": False, "pitch_shift": 1.5},
            "metadata": {"track_name": "Sample Track 2"}
        }
    ]
    
    # Perform batch processing
    results = client.process_batch_audio(sample_configs)
    for result in results:
        print(f"Audio {result['audio_path']}: {result['status']}")
    
    client.close()

if __name__ == "__main__":
    main()
