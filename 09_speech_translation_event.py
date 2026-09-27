"""Event-based synthesis: speech-to-speech translation (1:1, English -> Hindi) via the Synthesizing event."""
import os
from dotenv import load_dotenv
from playsound3 import playsound
from azure.identity import DefaultAzureCredential
import azure.cognitiveservices.speech as speech_sdk

load_dotenv()
foundry_endpoint = os.environ["SPEECH_ENDPOINT"].rstrip("/")
credential = DefaultAzureCredential()

# Collect audio chunks received via the Synthesizing event
audio_chunks = []


# Event handler: evt.result.audio is the Python equivalent of Result.GetAudio()
def synthesizing_handler(evt):
    audio_data = evt.result.audio
    if len(audio_data) > 0:
        print(f"[Synthesizing] Received {len(audio_data)} bytes of audio")
        audio_chunks.append(audio_data)


# Event-based synthesis: only supports 1:1 translation (single target language)
translation_cfg = speech_sdk.translation.SpeechTranslationConfig(
    token_credential=credential, endpoint=foundry_endpoint
)
translation_cfg.speech_recognition_language = "en-US"
translation_cfg.add_target_language("hi")
# Specify desired voice in TranslationConfig for event-based synthesis
translation_cfg.voice_name = "hi-IN-MadhurNeural"

audio_in_cfg = speech_sdk.AudioConfig(use_default_microphone=True)
translator = speech_sdk.translation.TranslationRecognizer(
    translation_config=translation_cfg, audio_config=audio_in_cfg
)
translator.synthesizing.connect(synthesizing_handler)

print("Ready to translate from", translation_cfg.speech_recognition_language)
print("Speak now...")
translation_result = translator.recognize_once_async().get()
print(f"Translating '{translation_result.text}'")
for lang, text in translation_result.translations.items():
    print(f"{lang}: '{text}'")

# The audio from the Synthesizing event is a WAV stream: save it and play it
if audio_chunks:
    output_file = "translation_hi.wav"
    with open(output_file, "wb") as f:
        f.write(b"".join(audio_chunks))
    print(f"Saved {output_file}, playing...")
    playsound(output_file)
else:
    print("No audio received.")
