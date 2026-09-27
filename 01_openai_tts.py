"""Speech generation (Text to Speech) using the OpenAI v1 API on Azure."""
import os
from pathlib import Path
from playsound3 import playsound
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Get Configuration Settings
load_dotenv()
endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
model_deployment = os.getenv("TTS_DEPLOYMENT", "gpt-4o-mini-tts")
speech_file_path = Path(__file__).parent / "speech.mp3"

# Keyless auth via Microsoft Entra ID
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

# Use the standard OpenAI client - just point base_url at your Azure endpoint + /openai/v1/
client = OpenAI(
    base_url=f"{endpoint}/openai/v1/",
    api_key=token_provider(),  # token used as a bearer key
)

# Generate speech and save to file
response = client.audio.speech.create(
    model=model_deployment,
    voice="vale",
    input="My name is Suresh Karri, and I am your AI teacher. Nice to meet you!",
    instructions="Speak in a serious tone.",
)
response.write_to_file(speech_file_path)
print(f"Saved {speech_file_path}")

# Play the generated speech file
playsound(str(speech_file_path))
