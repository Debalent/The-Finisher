from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pronouncing
import random

# Initialize FastAPI router
router = APIRouter()

# In-memory rhyme cache
RHYME_CACHE = {}

# Define input model for rhyme optimization
class RhymeInput(BaseModel):
    lyrics: str
    rhyme_scheme: str  # e.g., "AABB", "ABAB"

def get_rhyming_words(word):
    """
    🔹 Retrieves rhyming words for a given word using pronouncing library.
    - Caches results to improve performance.
    - Returns a list of rhyming words or empty list if none found.
    
    Args:
        word (str): The word to find rhymes for.
    
    Returns:
        list: List of rhyming words.
    """
    if word in RHYME_CACHE:
        return RHYME_CACHE[word]
    
    try:
        rhymes = pronouncing.rhymes(word.lower())
        RHYME_CACHE[word] = rhymes
        return rhymes
    except Exception as e:
        print(f"❌ Error finding rhymes for {word}: {e}")
        return []

def apply_rhyme_scheme(lyrics, rhyme_scheme):
    """
    🔹 Applies a rhyme scheme to lyrics by replacing end-of-line words.
    - Supports AABB and ABAB schemes.
    - Preserves original line structure.
    
    Args:
        lyrics (str): Lyrics with line breaks (\n).
        rhyme_scheme (str): Desired rhyme scheme (e.g., "AABB", "ABAB").
    
    Returns:
        str: Lyrics with rhyming words applied.
    """
    if rhyme_scheme not in ["AABB", "ABAB"]:
        raise ValueError("Unsupported rhyme scheme. Use 'AABB' or 'ABAB'.")

    lines = lyrics.strip().split('\n')
    if len(lines) < 2:
        return lyrics  # Too few lines to apply rhyme scheme

    optimized_lines = lines.copy()

    if rhyme_scheme == "AABB":
        for i in range(0, len(lines)-1, 2):
            if i + 1 < len(lines):
                word1 = lines[i].split()[-1].strip('.,!?')
                rhymes = get_rhyming_words(word1)
                if rhymes and i + 1 < len(lines):
                    word2 = lines[i+1].split()[-1].strip('.,!?')
                    if word2.lower() not in rhymes:
                        new_word = random.choice(rhymes) if rhymes else word2
                        optimized_lines[i+1] = ' '.join(lines[i+1].split()[:-1] + [new_word])

    elif rhyme_scheme == "ABAB":
        if len(lines) >= 4:
            # Rhyme lines 0 and 2, 1 and 3
            for pairs in [(0, 2), (1, 3)]:
                i, j = pairs
                if j < len(lines):
                    word1 = lines[i].split()[-1].strip('.,!?')
                    rhymes = get_rhyming_words(word1)
                    if rhymes:
                        word2 = lines[j].split()[-1].strip('.,!?')
                        if word2.lower() not in rhymes:
                            new_word = random.choice(rhymes) if rhymes else word2
                            optimized_lines[j] = ' '.join(lines[j].split()[:-1] + [new_word])

    return '\n'.join(optimized_lines)

@router.post("/optimize-rhymes")
def optimize_rhymes(input: RhymeInput):
    """
    🔹 API endpoint to optimize lyrics with a specified rhyme scheme.
    - Validates input and applies rhymes to lyrics.
    - Returns optimized lyrics.
    
    Args:
        input (RhymeInput): Lyrics and rhyme scheme.
    
    Returns:
        dict: Optimized lyrics and applied rhyme scheme.
    """
    try:
        optimized_lyrics = apply_rhyme_scheme(input.lyrics, input.rhyme_scheme)
        return {
            "optimized_lyrics": optimized_lyrics,
            "rhyme_scheme": input.rhyme_scheme
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing rhymes: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router, prefix="/api")
    uvicorn.run(app, host="0.0.0.0", port=8000)
