from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import os
import requests

app = FastAPI(title="The Finisher - MVP Backend")

# Allow requests from local files and any dev origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LyricsRequest(BaseModel):
    genre: Optional[str] = "pop"
    bpm: Optional[int] = 90
    mood: Optional[str] = "energetic"
    theme: Optional[str] = "love"


def simple_lyrics_generator(genre: str, bpm: int, mood: str, theme: str) -> str:
    # Minimal deterministic placeholder generator for MVP.
    lines = []
    intro = f"[{genre.capitalize()} | {bpm} BPM | {mood}]"
    lines.append(intro)
    lines.append(f"I been thinkin' 'bout {theme} every night,")
    lines.append("Beat steady knockin', got my feelings in the light.")
    lines.append("Words come easy when the rhythm's right,")
    lines.append(f"Hold on to the moment, this is our {mood} flight.")
    lines.append("")
    lines.append("Hook:")
    lines.append(f"Finish what we started, make the story bright,")
    lines.append(f"Turn the spark to fire, take this song to life.")
    lines.append("No more waiting, this is our time,")
    lines.append(f"{theme.capitalize()} in the chorus, let the stars align.")

    return "\n".join(lines)


def openai_generate(prompt: str, api_key: str) -> str:
    # Minimal OpenAI call wrapper — uses the completions endpoint pattern.
    # This is intentionally simple; for production use the official OpenAI SDK and robust error handling.
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 300,
        'temperature': 0.8,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    try:
        return data['choices'][0]['message']['content'].strip()
    except Exception:
        return '\n'.join([choice.get('text', '') for choice in data.get('choices', [])])


@app.post("/api/lyrics/generate")
async def generate_lyrics(req: LyricsRequest):
    provider = os.getenv('MODEL_PROVIDER', 'local')
    if provider == 'openai' and os.getenv('OPENAI_API_KEY'):
        prompt = f"Write lyrics in the style of {req.genre} at {req.bpm} bpm with a {req.mood} mood about {req.theme}. Keep it 8-16 lines."
        try:
            lyrics = openai_generate(prompt, os.getenv('OPENAI_API_KEY'))
            return {"lyrics": lyrics, "timestamp": datetime.utcnow().isoformat() + "Z", "provider": "openai"}
        except Exception as e:
            # fallback to local generator on failure
            print('OpenAI generation failed:', e)

    lyrics = simple_lyrics_generator(req.genre, req.bpm, req.mood, req.theme)
    return {"lyrics": lyrics, "timestamp": datetime.utcnow().isoformat() + "Z", "provider": "local"}
