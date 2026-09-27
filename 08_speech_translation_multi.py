"""Speak English once, get French and Hindi translations, then hear them spoken (manual synthesis)."""
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
import azure.cognitiveservices.speech as speech_sdk

load_dotenv()
foundry_endpoint = os.environ["SPEECH_ENDPOINT"].rstrip("/")
credential = DefaultAzureCredential()

translation_cfg = speech_sdk.translation.SpeechTranslationConfig(
    token_credential=credential, endpoint=foundry_endpoint
)
translation_cfg.speech_recognition_language = "en-US"
translation_cfg.add_target_language("fr")
translation_cfg.add_target_language("hi")

audio_in_cfg = speech_sdk.AudioConfig(use_default_microphone=True)
translator = speech_sdk.translation.TranslationRecognizer(
    translation_config=translation_cfg, audio_config=audio_in_cfg
)
print("Ready to translate from", translation_cfg.speech_recognition_language)

# Configure speech for synthesis of translations
speech_cfg = speech_sdk.SpeechConfig(token_credential=credential, endpoint=foundry_endpoint)
voices = {"fr": "fr-FR-HenriNeural", "hi": "hi-IN-MadhurNeural"}

# Translate user speech
print("Speak now...")
translation_results = translator.recognize_once_async().get()
if translation_results.reason != speech_sdk.ResultReason.TranslatedSpeech:
    raise SystemExit(f"Translation failed: {translation_results.reason}")
print(f"Translating '{translation_results.text}'")

# Print and speak the translation results
translations = translation_results.translations
for lang in translations:
    print(f"{lang}: '{translations[lang]}'")
    speech_cfg.speech_synthesis_voice_name = voices.get(lang)
    audio_out_cfg = speech_sdk.audio.AudioOutputConfig(use_default_speaker=True)
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_cfg, audio_out_cfg)
    speak = speech_synthesizer.speak_text_async(translations[lang]).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)
