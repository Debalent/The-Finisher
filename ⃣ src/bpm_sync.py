import syllapy

def add_line_breaks(lyrics, bpm=120, base_syllables=8):
    """
    🔹 Splits lyrics into lines based on syllable count, adjusted for BPM.
    - Aims for a target syllable count per line, modified by BPM for singability.
    - Returns lyrics with line breaks (\n) for song structure.
    
    Args:
        lyrics (str): The raw lyrics as a string.
        bpm (int): Beats per minute to adjust syllable count (default: 120).
        base_syllables (int): Base syllable count per line for BPM=120 (default: 8).
    
    Returns:
        str: Lyrics with line breaks added.
    """
    # Adjust syllables per line based on BPM
    # Higher BPM -> fewer syllables, lower BPM -> more syllables
    syllables_per_line = int(base_syllables * (120 / bpm))
    syllables_per_line = max(6, min(12, syllables_per_line))  # Cap between 6 and 12

    words = lyrics.split()
    lines = []
    current_line = []
    current_syllables = 0

    for word in words:
        word_syllables = syllapy.count(word)
        if current_syllables + word_syllables <= syllables_per_line:
            current_line.append(word)
            current_syllables += word_syllables
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_syllables = word_syllables

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)

def add_timestamps(lyrics, bpm):
    """
    🔹 Placeholder for adding timestamps to lyrics for .lrc file generation.
    - Assumes 4 beats per line in 4/4 time signature.
    - To be implemented for DAW/karaoke integration.
    
    Args:
        lyrics (str): Lyrics with line breaks.
        bpm (int): Beats per minute for timing calculation.
    
    Returns:
        list: List of (timestamp, line) tuples (currently placeholder).
    """
    # Placeholder implementation
    # Future: Calculate seconds_per_beat = 60 / BPM, seconds_per_line = 4 * seconds_per_beat
    return [(0, line) for line in lyrics.split('\n')]

if __name__ == "__main__":
    # Example usage
    sample_lyrics = "Your love shines bright in the morning light dancing to the beat of our hearts"
    bpm = 120
    synchronized_lyrics = add_line_breaks(sample_lyrics, bpm=bpm)
    print(f"\nSynchronized Lyrics (BPM={bpm}):\n{synchronized_lyrics}")

    # Test with different BPMs
    for test_bpm in [80, 140]:
        synchronized_lyrics = add_line_breaks(sample_lyrics, bpm=test_bpm)
        print(f"\nSynchronized Lyrics (BPM={test_bpm}):\n{synchronized_lyrics}")
