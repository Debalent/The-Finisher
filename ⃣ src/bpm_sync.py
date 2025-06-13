import syllapy

def count_syllables(lyrics):
    return sum(syllapy.count(word) for word in lyrics.split())

# Example usage
lyrics = "I never thought I'd see the day"
syllable_count = count_syllables(lyrics)
print(f"Syllables: {syllable_count}")
