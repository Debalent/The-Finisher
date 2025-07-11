import syllables

def add_line_breaks(lyrics, syllables_per_line=8):
    """
    Splits the given lyrics into lines based on syllable count.
    
    Args:
        lyrics (str): The raw lyrics as a string.
        syllables_per_line (int): The target number of syllables per line (default is 8).
    
    Returns:
        str: The lyrics with line breaks added.
    """
    words = lyrics.split()
    lines = []
    current_line = []
    current_syllables = 0
    
    for word in words:
        word_syllables = syllables.estimate(word)
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

if __name__ == "__main__":
    sample_lyrics = "Your love shines bright in the morning light dancing to the beat of our hearts"
    synchronized_lyrics = add_line_breaks(sample_lyrics)
    print(synchronized_lyrics)
