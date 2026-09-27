"""Multimodal reasoning over audio: ask a question about an audio file (not just transcribe it).

Requires a gpt-audio-mini (or gpt-audio) deployment. Run 01_openai_tts.py first to create speech.mp3.
"""
import base64
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()
client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["SPEECH_KEY"],
    api_version="2025-04-01-preview",
)

audio_b64 = base64.b64encode((Path(__file__).parent / "speech.mp3").read_bytes()).decode()

response = client.chat.completions.create(
    model=os.getenv("AUDIO_CHAT_DEPLOYMENT", "gpt-audio-mini"),
    modalities=["text"],
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "summarize this audio for me"},
            {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}},
        ],
    }],
)
print(response.choices[0].message.content)
