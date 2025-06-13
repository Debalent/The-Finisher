import requests

def get_rhymes(word):
    response = requests.get(f"https://api.datamuse.com/words?rel_rhy={word}")
    return [word["word"] for word in response.json()]

# Example usage
word = "love"
rhymes = get_rhymes(word)
print(f"Words that rhyme with '{word}': {rhymes}")
