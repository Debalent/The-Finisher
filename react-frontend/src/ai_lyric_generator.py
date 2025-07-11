from fastapi import FastAPI
from pydantic import BaseModel
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch

# Initialize the FastAPI application
app = FastAPI()

# Define the input model for the API endpoint
class LyricInput(BaseModel):
    genre: str
    mood: str
    bpm: int
    theme: str

# Load the pre-trained model and tokenizer
# Using default GPT-2; replace with a fine-tuned model like "bigjoedata/rockbot355M" for specific genres
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Define the API endpoint for generating lyrics
@app.post("/generate-lyrics")
def generate_lyrics(input: LyricInput):
    # Construct the prompt based on user inputs
    prompt = f"Generate a {input.genre} song with {input.mood} emotion and {input.bpm} BPM about {input.theme}. Lyrics: "
    
    # Tokenize the prompt
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=50)
    
    # Generate lyrics using the model
    sample_outputs = model.generate(
        **inputs,
        do_sample=True,
        max_length=150,  # Adjust for desired lyric length
        top_p=0.92,      # Nucleus sampling for diverse outputs
        top_k=0,
        temperature=0.6, # Control creativity
        num_return_sequences=1,
        no_repeat_ngram_size=2  # Prevent repetitive phrases
    )
    
    # Decode the generated text
    generated_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)
    
    # Remove the prompt from the generated text
    generated_lyrics = generated_text[len(prompt):]
    
    return {"lyrics": generated_lyrics}

# Run the FastAPI application (if running locally)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
