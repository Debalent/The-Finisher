# src/voice/voice_api.py

import os
import requests

# Retrieve API credentials (make sure to set these environment variables)
API_KEY = os.getenv("VOICE_API_KEY")
API_URL = os.getenv("VOICE_API_URL")

def send_audio_for_processing(audio_path: str):
    """
    Sends an audio file to the voice API for processing.
    """
    try:
        with open(audio_path, "rb") as audio_file:
            files = {"audio": audio_file}
            headers = {"Authorization": f"Bearer {API_KEY}"}
            response = requests.post(API_URL, headers=headers, files=files)
            response.raise_for_status()  # Raise an error for bad status codes
            return response.json()
    except Exception as e:
        print("Error processing audio:", e)
        return None
