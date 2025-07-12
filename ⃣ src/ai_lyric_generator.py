from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
from backend.db.database import get_db, get_user_subscription, insert_lyric
from src.bpm_sync import add_line_breaks

# Initialize FastAPI router
router = APIRouter()

# Define input model for lyric generation
class LyricInput(BaseModel):
    user_id: int
    genre: str
    mood: str
    bpm: int
    theme: str

# Load Hugging Face model and tokenizer
# Using default GPT-2; replace with 'SpartanCinder/GPT2-finetuned-lyric-generation' for better lyrics
model_name = "gpt2"
try:
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)
except Exception as e:
    print(f"❌ Error loading model: {e}")
    tokenizer = None
    model = None

@router.post("/generate-lyrics")
def generate_lyrics(input: LyricInput, db=Depends(get_db)):
    """
    🔹 Generates lyrics based on user inputs and stores them in the database.
    - Validates user subscription.
    - Uses Hugging Face GPT-2 for generation.
    - Applies BPM synchronization with line breaks.
    - Stores lyrics in the database.
    """
    # Check if model and tokenizer are loaded
    if not tokenizer or not model:
        raise HTTPException(status_code=500, detail="Model not initialized")

    # Verify user subscription
    subscription = get_user_subscription(input.user_id)
    if not subscription:
        raise HTTPException(status_code=403, detail="No active subscription found")

    # Construct prompt
    prompt = f"Generate a {input.genre} song with {input.mood} emotion and {input.bpm} BPM about {input.theme}. Lyrics: "

    try:
        # Tokenize prompt
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=50)

        # Generate lyrics
        sample_outputs = model.generate(
            **inputs,
            do_sample=True,
            max_length=150,
            top_p=0.92,
            top_k=0,
            temperature=0.6,
            num_return_sequences=1,
            no_repeat_ngram_size=2
        )

        # Decode generated text
        generated_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)
        raw_lyrics = generated_text[len(prompt):].strip()

        # Apply BPM synchronization
        synchronized_lyrics = add_line_breaks(raw_lyrics, syllables_per_line=8)

        # Store lyrics in database
        lyric_id = insert_lyric(
            user_id=input.user_id,
            text=synchronized_lyrics,
            mood=input.mood,
            genre=input.genre,
            bpm=input.bpm
        )

        if not lyric_id:
            raise HTTPException(status_code=500, detail="Failed to store lyrics in database")

        return {
            "lyrics": synchronized_lyrics,
            "lyric_id": lyric_id,
            "plan": subscription['plan_name']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lyrics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router, prefix="/api")
    uvicorn.run(app, host="0.0.0.0", port=8000)
