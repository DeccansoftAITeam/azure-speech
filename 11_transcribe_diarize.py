"""Speaker diarization: transcribe a conversation and label who said what (gpt-4o-transcribe-diarize).

Creates a two-speaker conversation with SSML (if missing), then transcribes it with speaker labels.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speechsdk

load_dotenv()
audio_path = Path(__file__).parent / "conversation.wav"

# 1. Create a sample two-person conversation using SSML with two voices
if not audio_path.exists():
    ssml = """
<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
  <voice name='en-US-AndrewNeural'>Hi Emma, did you finish the Azure speech lab?</voice>
  <voice name='en-US-EmmaNeural'>Yes, I did. The translation demo was my favourite part.</voice>
  <voice name='en-US-AndrewNeural'>Great. Can you show me how diarization works tomorrow?</voice>
  <voice name='en-US-EmmaNeural'>Sure, let's meet at ten in the morning.</voice>
</speak>"""
    speech_config = speechsdk.SpeechConfig(subscription=os.environ["SPEECH_KEY"],
                                           endpoint=os.environ["SPEECH_ENDPOINT"])
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=speechsdk.audio.AudioOutputConfig(filename=str(audio_path)))
    synthesizer.speak_ssml_async(ssml).get()
    del synthesizer
    print(f"Created {audio_path.name}")

# 2. Transcribe with speaker labels
client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["SPEECH_KEY"],
    api_version="2025-04-01-preview",
)
with open(audio_path, "rb") as f:
    result = client.audio.transcriptions.create(
        model=os.getenv("DIARIZE_DEPLOYMENT", "gpt-4o-transcribe-diarize"),
        file=f,
        response_format="diarized_json",
        chunking_strategy="auto",
    )

for seg in result.segments:
    print(f"[{seg.start:5.1f}s - {seg.end:5.1f}s] Speaker {seg.speaker}: {seg.text}")
