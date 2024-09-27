import requests
import json
from pydub import AudioSegment

import random
def get_audio(text:str, voice_id:str="us-male-2", model:str="style-diff-500")->str: #returns path to saved audio file
    response = requests.request(
    method="POST",
    url="https://api.neets.ai/v1/tts",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": "1bac98feba5348abbd2cd66cfdda612f"
    },
    json={
        "text": text,
        "voice_id": voice_id,
        "params": {
            "model": model
        }
    }
    )
    #filename is random
    filename = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename


def get_audio_length(filename: str) -> float:
    audio = AudioSegment.from_file(filename)
    duration_seconds = len(audio) / 1000.0
    return duration_seconds

    