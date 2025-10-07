from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import os
import logging
from dotenv import load_dotenv
import openai
import stripe

from . import db

load_dotenv()

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger('the-finisher')

app = FastAPI(title="The Finisher - MVP Backend")

# Configure CORS from environment variable (comma-separated) for production safety
allowed = os.getenv('ALLOWED_ORIGINS', '')
if allowed:
    origins = [o.strip() for o in allowed.split(',') if o.strip()]
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


def openai_generate(prompt: str) -> str:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not set')
    openai.api_key = api_key
    # Use the official OpenAI SDK
    resp = openai.ChatCompletion.create(
        model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.8')),
    )
    return resp.choices[0].message.content.strip()


@app.on_event('startup')
def startup_event():
    # Initialize DB
    try:
        db.init_db()
        logger.info('Database initialized')
    except Exception as e:
        logger.exception('Failed to init DB: %s', e)


@app.post("/api/lyrics/generate")
async def generate_lyrics(req: LyricsRequest):
    provider = os.getenv('MODEL_PROVIDER', 'local')
    lyrics = None
    provider_used = 'local'

    if provider == 'openai':
        try:
            prompt = f"Write lyrics in the style of {req.genre} at {req.bpm} bpm with a {req.mood} mood about {req.theme}. Keep it 8-16 lines."
            lyrics = openai_generate(prompt)
            provider_used = 'openai'
        except Exception as e:
            logger.exception('OpenAI generation failed: %s', e)

    if not lyrics:
        lyrics = simple_lyrics_generator(req.genre, req.bpm, req.mood, req.theme)

    # Save generated lyrics
    try:
        record = db.save_lyric(req.genre, req.bpm, req.mood, req.theme, lyrics, provider_used)
    except Exception as e:
        logger.exception('Failed to save lyric: %s', e)

    return {"lyrics": lyrics, "timestamp": datetime.utcnow().isoformat() + "Z", "provider": provider_used}



@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/api/lyrics/recent')
def recent_lyrics(limit: int = 10):
    try:
        items = db.get_recent(limit)
        return {'items': [item.dict() for item in items]}
    except Exception as e:
        logger.exception('Failed to fetch recent lyrics: %s', e)
        raise HTTPException(status_code=500, detail='DB error')


# Stripe skeleton endpoints
stripe_api_key = os.getenv('STRIPE_API_KEY')
if stripe_api_key:
    stripe.api_key = stripe_api_key


@app.post('/api/create-checkout-session')
async def create_checkout():
    if not stripe_api_key:
        raise HTTPException(status_code=500, detail='Stripe not configured')
    # Simple placeholder; in production you'd accept a price param or plan id
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': os.getenv('STRIPE_PRICE_ID'),
                'quantity': 1,
            }],
            success_url=os.getenv('STRIPE_SUCCESS_URL', 'https://example.com/success'),
            cancel_url=os.getenv('STRIPE_CANCEL_URL', 'https://example.com/cancel'),
        )
        return {'url': session.url}
    except Exception as e:
        logger.exception('Stripe error: %s', e)
        raise HTTPException(status_code=500, detail='Stripe error')

