import logging
from typing import Optional
from pydub import AudioSegment

# 🔹 Configure logging for clarity and vibe
logging.basicConfig(level=logging.INFO, format="🎵 %(levelname)s: %(message)s")

# 🔹 Constants for volume adjustment
DEFAULT_GAIN_DB = -3

def load_audio(file_path: str) -> Optional[AudioSegment]:
    """
    🔹 Load an audio file from the given path.
    - Supports formats like MP3, WAV, etc.
    - Returns an AudioSegment or None if loading fails.
    """
    try:
        audio = AudioSegment.from_file(file_path)
        logging.info(f"✅ Loaded audio: {file_path}")
        return audio
    except Exception as e:
        logging.error(f"❌ Failed to load '{file_path}': {e}")
        return None

def normalize_audio(audio: AudioSegment) -> AudioSegment:
    """
    🔹 Normalize volume for consistency.
    - Returns a normalized AudioSegment.
    """
    try:
        normalized = audio.normalize()
        logging.info("✅ Audio normalized")
        return normalized
    except Exception as e:
        logging.error(f"❌ Normalization failed: {e}")
        return audio

def mix_tracks(
    track1_path: str,
    track2_path: str,
    output_path: str,
    output_format: str = "mp3",
    gain_db: int = DEFAULT_GAIN_DB,
    normalize: bool = True
) -> None:
    """
    🔹 Mix two audio tracks and export the result.
    - Applies optional volume adjustments and mastering.
    """
    track1 = load_audio(track1_path)
    track2 = load_audio(track2_path)

    if not track1 or not track2:
        logging.error("🚫 Cannot mix: one or both tracks failed to load.")
        return

    # 🔹 Adjust gain for balance
    track1 = track1 + gain_db
    track2 = track2 + gain_db

    # 🔹 Mix tracks together
    mixed = track1.overlay(track2)

    # 🔹 Apply optional mastering
    final_mix = normalize_audio(mixed) if normalize else mixed

    # 🔹 Export final track
    try:
        final_mix.export(output_path, format=output_format)
        logging.info(f"🎶 Exported final mix to '{output_path}' as {output_format}")
    except Exception as e:
        logging.error(f"❌ Export failed: {e}")

def main() -> None:
    # ✨ Customize your input/output paths here
    track1_path = "audio/intro.mp3"
    track2_path = "audio/verse.mp3"
    output_path = "audio/final_mix.mp3"

    mix_tracks(track1_path, track2_path, output_path)

if __name__ == "__main__":
    main()
