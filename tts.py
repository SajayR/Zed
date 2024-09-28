import requests
import json
from pydub import AudioSegment

import random
def get_audio(text:str, voice_id:str="us-male-2", model:str="ar-diff-50k")->str: #returns path to saved audio file
    response = requests.request(
    method="POST",
    url="https://api.neets.ai/v1/tts",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": "c4ddea5a952a415d87a79e41177e4da8"
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
    import os

    audio_folder = "/Users/cisco/Documents/CisStuff/corny/audio"
    filename = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10)) + ".mp3"
    full_path = os.path.join(audio_folder, filename)
    
    os.makedirs(audio_folder, exist_ok=True)
    
    with open(full_path, "wb") as f:
        f.write(response.content)
    return full_path


def get_audio_length(filename: str) -> float:
    audio = AudioSegment.from_file(filename)
    duration_seconds = len(audio) / 1000.0
    return duration_seconds

    