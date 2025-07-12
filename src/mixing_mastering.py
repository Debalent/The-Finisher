"""
Module for advanced audio processing in The Finisher.

This module provides robust audio mixing, mastering, and effect application capabilities,
designed for scalability and seamless integration with creative workflows.
"""

import logging
from typing import Optional, List, Dict, Any
from pydub import AudioSegment
from pydantic import BaseModel, Field, ValidationError
import os
import yaml
from datetime import datetime
from retry import retry

# Configure logging for operational insights and user-friendly output
logging.basicConfig(
    filename='audio_processor.log',
    level=logging.INFO,
    format='%(asctime)s - 🎵 %(levelname)s: %(message)s'
)

# Load configuration from environment variables or YAML for flexible deployment
CONFIG_FILE = os.getenv('AUDIO_CONFIG', 'audio_config.yaml')
try:
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f) or {}
except FileNotFoundError:
    config = {}
    logging.warning("Configuration file not found, using default settings")

# Constants for audio processing, configurable via YAML or environment
DEFAULT_GAIN_DB = config.get('DEFAULT_GAIN_DB', float(os.getenv('DEFAULT_GAIN_DB', -3)))
DEFAULT_OUTPUT_FORMAT = config.get('DEFAULT_OUTPUT_FORMAT', os.getenv('DEFAULT_OUTPUT_FORMAT', 'mp3'))
DEFAULT_FADE_IN_MS = config.get('DEFAULT_FADE_IN_MS', int(os.getenv('DEFAULT_FADE_IN_MS', 1000)))
DEFAULT_FADE_OUT_MS = config.get('DEFAULT_FADE_OUT_MS', int(os.getenv('DEFAULT_FADE_OUT_MS', 1000)))
DEFAULT_CROSSFADE_MS = config.get('DEFAULT_CROSSFADE_MS', int(os.getenv('DEFAULT_CROSSFADE_MS', 500)))
SUPPORTED_FORMATS = config.get('SUPPORTED_FORMATS', ['mp3', 'wav', 'ogg', 'flac'])

# Pydantic model for audio processing configuration validation
class AudioMixConfig(BaseModel):
    track_paths: List[str] = Field(..., min_items=1)
    output_path: str = Field(..., min_length=1)
    output_format: str = Field(default=DEFAULT_OUTPUT_FORMAT, pattern=f"^(?:{'|'.join(SUPPORTED_FORMATS)})$")
    gain_db: float = Field(default=DEFAULT_GAIN_DB, ge=-20, le=20)
    normalize: bool = Field(default=True)
    fade_in_ms: int = Field(default=DEFAULT_FADE_IN_MS, ge=0)
    fade_out_ms: int = Field(default=DEFAULT_FADE_OUT_MS, ge=0)
    crossfade_ms: int = Field(default=DEFAULT_CROSSFADE_MS, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AudioProcessor:
    """Scalable audio processing class for mixing, mastering, and applying effects."""
    
    def __init__(self):
        self.supported_formats = SUPPORTED_FORMATS
        logging.info("AudioProcessor initialized with supported formats: %s", self.supported_formats)

    def load_audio(self, file_path: str) -> Optional[AudioSegment]:
        """
        Load an audio file with error handling and format validation.
        
        Args:
            file_path (str): Path to the audio file.
            
        Returns:
            Optional[AudioSegment]: Loaded audio segment or None if loading fails.
        """
        try:
            if not os.path.exists(file_path):
                logging.error(f"File not found: {file_path}")
                return None
            audio = AudioSegment.from_file(file_path)
            logging.info(f"Loaded audio: {file_path} (duration: {len(audio)/1000:.2f}s)")
            return audio
        except Exception as e:
            logging.error(f"Failed to load '{file_path}': {e}")
            return None

    def normalize_audio(self, audio: AudioSegment) -> AudioSegment:
        """
        Normalize audio volume for consistent output, critical for professional-grade results.
        
        Args:
            audio (AudioSegment): Input audio segment.
            
        Returns:
            AudioSegment: Normalized audio segment.
        """
        try:
            normalized = audio.normalize()
            logging.info("Audio normalized successfully")
            return normalized
        except Exception as e:
            logging.error(f"Normalization failed: {e}")
            return audio

    def apply_fades(self, audio: AudioSegment, fade_in_ms: int, fade_out_ms: int) -> AudioSegment:
        """
        Apply fade-in and fade-out effects for smooth transitions, enhancing user experience.
        
        Args:
            audio (AudioSegment): Input audio segment.
            fade_in_ms (int): Fade-in duration in milliseconds.
            fade_out_ms (int): Fade-out duration in milliseconds.
            
        Returns:
            AudioSegment: Audio with applied fades.
        """
        try:
            if fade_in_ms > 0:
                audio = audio.fade_in(fade_in_ms)
                logging.info(f"Applied fade-in: {fade_in_ms}ms")
            if fade_out_ms > 0:
                audio = audio.fade_out(fade_out_ms)
                logging.info(f"Applied fade-out: {fade_out_ms}ms")
            return audio
        except Exception as e:
            logging.error(f"Failed to apply fades: {e}")
            return audio

    @retry(Exception, tries=3, delay=1, backoff=2)
    def export_audio(self, audio: AudioSegment, output_path: str, output_format: str) -> bool:
        """
        Export audio with retry logic for reliability in production environments.
        
        Args:
            audio (AudioSegment): Audio segment to export.
            output_path (str): Path to save the output file.
            output_format (str): Format for the output file.
            
        Returns:
            bool: True if export succeeds, False otherwise.
        """
        try:
            audio.export(output_path, format=output_format, tags={"created_by": "The Finisher"})
            logging.info(f"Exported audio to '{output_path}' as {output_format}")
            return True
        except Exception as e:
            logging.error(f"Export failed for '{output_path}': {e}")
            raise

    def mix_tracks(self, config: Dict[str, Any]) -> bool:
        """
        Mix multiple audio tracks with advanced processing, optimized for creative workflows.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary for mixing.
            
        Returns:
            bool: True if mixing and export succeed, False otherwise.
        """
        try:
            # Validate configuration
            mix_config = AudioMixConfig(**config)
            logging.info(f"Validated mix configuration for output: {mix_config.output_path}")

            # Load and validate all tracks
            tracks = [self.load_audio(path) for path in mix_config.track_paths]
            if not all(tracks):
                logging.error("Cannot mix: one or more tracks failed to load")
                return False

            # Apply gain adjustments
            tracks = [track + mix_config.gain_db for track in tracks]
            logging.info(f"Applied gain: {mix_config.gain_db}dB to {len(tracks)} tracks")

            # Mix tracks with optional crossfade
            mixed = tracks[0]
            for i, track in enumerate(tracks[1:], 1):
                if mix_config.crossfade_ms > 0:
                    mixed = mixed.append(track, crossfade=mix_config.crossfade_ms)
                    logging.info(f"Applied crossfade: {mix_config.crossfade_ms}ms at track {i+1}")
                else:
                    mixed = mixed.overlay(track)
                    logging.info(f"Overlaid track {i+1}")

            # Apply normalization and fades
            if mix_config.normalize:
                mixed = self.normalize_audio(mixed)
            mixed = self.apply_fades(mixed, mix_config.fade_in_ms, mix_config.fade_out_ms)

            # Export with metadata
            success = self.export_audio(mixed, mix_config.output_path, mix_config.output_format)
            if success:
                mix_config.metadata.update({"created_at": datetime.utcnow().isoformat()})
                logging.info(f"Metadata applied: {mix_config.metadata}")
            return success

        except ValidationError as e:
            logging.error(f"Configuration validation failed: {e}")
            return False
        except Exception as e:
            logging.error(f"Mixing failed: {e}")
            return False

def main() -> None:
    """Main function demonstrating advanced audio processing capabilities."""
    processor = AudioProcessor()
    
    # Sample configuration for demonstration
    mix_config = {
        "track_paths": ["audio/intro.mp3", "audio/verse.mp3"],
        "output_path": "audio/final_mix.mp3",
        "output_format": "mp3",
        "gain_db": DEFAULT_GAIN_DB,
        "normalize": True,
        "fade_in_ms": DEFAULT_FADE_IN_MS,
        "fade_out_ms": DEFAULT_FADE_OUT_MS,
        "crossfade_ms": DEFAULT_CROSSFADE_MS,
        "metadata": {"artist": "Demo Artist", "title": "Final Mix"}
    }
    
    success = processor.mix_tracks(mix_config)
    print(f"Mix {'successful' if success else 'failed'}")

if __name__ == "__main__":
    main()
