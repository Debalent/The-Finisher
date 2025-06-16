import logging
from pydub import AudioSegment

# 🔹 Configure logging for better debugging and investor clarity
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def load_audio(file_path):
    """
    🔹 Load an audio file from the given path.
    - Supports multiple formats (MP3, WAV, etc.).
    - Returns an AudioSegment object for further processing.
    """
    try:
        audio = AudioSegment.from_file(file_path)
        logging.info(f"✅ Loaded audio: {file_path}")
        return audio
    except Exception as e:
        logging.error(f"❌ Error loading audio from {file_path}: {e}")
        return None

def normalize_audio(audio):
    """
    🔹 Normalize an audio segment to simulate basic mastering.
    - Ensures consistent volume levels across tracks.
    """
    try:
        normalized = audio.normalize()
        logging.info("✅ Audio normalized successfully")
        return normalized
    except Exception as e:
        logging.error(f"❌ Error normalizing audio: {e}")
        return audio

def mix_tracks(track1_path, track2_path, output_path, output_format="mp3"):
    """
    🔹 Mix two audio tracks together and export the final mastered track.
    - Applies basic volume balancing before overlaying.
    - Supports multiple output formats (MP3, WAV, etc.).
    """
    track1 = load_audio(track1_path)
    track2 = load_audio(track2_path)

    if track1 is None or track2 is None:
        logging.error("❌ Unable to load one or both tracks. Check file paths.")
        return

    # 🔹 Adjust volume levels for better balance
    track1 = track1 - 3
    track2 = track2 - 3

    # 🔹 Overlay the second track onto the first (basic mixing strategy)
    mixed_track = track1.overlay(track2)

    # 🔹 Apply mastering by normalizing the final mix
    final_mix = normalize_audio(mixed_track)

    try:
        # 🔹 Export the mastered mix in the specified format
        final_mix.export(output_path, format=output_format)
        logging.info(f"✅ Mixed and mastered track exported successfully to: {output_path}")
    except Exception as e:
        logging.error(f"❌ Error exporting the mix: {e}")

def main():
    # 🔹 Example usage: Update paths based on your project structure
    track1_path = "path/to/track1.mp3"
    track2_path = "path/to/track2.mp3"
    output_path = "path/to/final_mix.mp3"
    
    mix_tracks(track1_path, track2_path, output_path, output_format="mp3")

if __name__ == "__main__":
    main()
