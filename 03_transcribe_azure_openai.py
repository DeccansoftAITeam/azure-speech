"""Speech to Text (transcription) using the AzureOpenAI client. Run 01_openai_tts.py first to create speech.mp3."""
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()
endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
model_deployment = os.getenv("TRANSCRIBE_DEPLOYMENT", "gpt-4o-mini-transcribe")
speech_file_path = Path(__file__).parent / "speech.mp3"

# Create the Azure OpenAI client
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)
client = AzureOpenAI(
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider,
    api_version="2025-03-01-preview",
)

# Call model to transcribe audio file
with open(speech_file_path, "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model=model_deployment,
        file=audio_file,
        response_format="text",
    )
print(transcription)
