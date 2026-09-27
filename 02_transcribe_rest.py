"""Speech to Text (transcription) using the REST API. Run 01_openai_tts.py first to create speech.mp3."""
import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()
endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
deployment = os.getenv("TRANSCRIBE_DEPLOYMENT", "gpt-4o-mini-transcribe")
speech_file_path = Path(__file__).parent / "speech.mp3"

token = DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default").token

url = f"{endpoint}/openai/deployments/{deployment}/audio/transcriptions?api-version=2025-03-01-preview"
headers = {"Authorization": f"Bearer {token}"}

with open(speech_file_path, "rb") as f:
    files = {"file": ("speech.mp3", f, "audio/mpeg")}
    data = {"response_format": "text"}
    r = requests.post(url, headers=headers, files=files, data=data)

print(r.status_code)
print(r.text)
