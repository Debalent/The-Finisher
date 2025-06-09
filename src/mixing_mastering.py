# src/mixing_mastering.py
"""
Module for Mixing and Mastering Audio within The Finisher.

This module provides basic functions to:
- Load audio files
- Apply a normalization process to simulate mastering
- Mix two audio tracks together (e.g., overlaying vocals over an instrumental track)
"""

from pydub import AudioSegment

def load_audio(file_path):
    """
    Load an audio file located at file_path.
    
    Args:
        file_path (str): Path to the audio file.
    
    Returns:
        AudioSegment: Loaded audio segment or None if loading fails.
    """
    try:
        audio = AudioSegment.from_file(file_path)
        return audio
    except Exception as e:
        print(f"Error loading audio from {file_path}: {e}")
        return None

def normalize_audio(audio):
    """
    Normalize an audio segment, simulating a basic mastering process.
    
    Args:
        audio (AudioSegment): The audio segment to normalize.
        
    Returns:
        AudioSegment: Normalized audio segment.
    """
    try:
        normalized = audio.normalize()
        return normalized
    except Exception as e:
        print(f"Error normalizing audio: {e}")
        return audio

def mix_tracks(track1_path, track2_path, output_path):
    """
    Mix two audio tracks together and export the final mastered track.
    
    Args:
        track1_path (str): File path of the first track.
        track2_path (str): File path of the second track.
        output_path (str): File path for exporting the mixed track.
    """
    track1 = load_audio(track1_path)
    track2 = load_audio(track2_path)
    
    if track1 is None or track2 is None:
        print("Unable to load one or both of the tracks. Please check the file paths.")
        return
    
    # Optionally adjust volumes for each track (simulate basic balance)
    track1 = track1 - 3  # reduce volume slightly
    track2 = track2 - 3  # reduce volume slightly
    
    # Overlay the second track over the first (this is a simple mixing strategy)
    mixed_track = track1.overlay(track2)
    
    # Apply mastering by normalizing the final mix
    final_mix = normalize_audio(mixed_track)
    
    try:
        # Export the mastered mix (you can change the format as needed, e.g., "wav" or "mp3")
        final_mix.export(output_path, format="mp3")
        print(f"Mixed and mastered track exported successfully to: {output_path}")
    except Exception as e:
        print(f"Error exporting the mix: {e}")

def main():
    # Example usage: update these paths based on your project directory structure
    track1_path = "path/to/track1.mp3"  # e.g., instrumental track
    track2_path = "path/to/track2.mp3"  # e.g., vocal track
    output_path = "path/to/final_mix.mp3"
    mix_tracks(track1_path, track2_path, output_path)

if __name__ == "__main__":
    main()
