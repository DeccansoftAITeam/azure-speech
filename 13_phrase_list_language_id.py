"""Speech SDK extras: automatic language identification and phrase lists.

1. Language identification: detect which of the candidate languages is being spoken.
2. Phrase list: boost recognition of names/jargon the model might otherwise miss (no training needed).
"""
import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv()
speech_config = speechsdk.SpeechConfig(subscription=os.environ["SPEECH_KEY"],
                                       endpoint=os.environ["SPEECH_ENDPOINT"])

# Create a Hindi sample file so the demo works without a microphone
sample = "hindi_sample.wav"
speech_config.speech_synthesis_voice_name = "hi-IN-SwaraNeural"
synth = speechsdk.SpeechSynthesizer(speech_config=speech_config,
                                    audio_config=speechsdk.audio.AudioOutputConfig(filename=sample))
synth.speak_text_async("नमस्ते, मैं Azure स्पीच सर्विस सीख रहा हूँ।").get()
del synth

use_mic = input("Use microphone? (y/N): ").strip().lower() == "y"


def audio_config():
    if use_mic:
        print("Speak now...")
        return speechsdk.audio.AudioConfig(use_default_microphone=True)
    return speechsdk.audio.AudioConfig(filename=sample)


# 1. Automatic language identification (up to 4 candidates at start of audio)
auto_detect = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
    languages=["en-US", "hi-IN", "fr-FR", "es-ES"])
recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,
                                        auto_detect_source_language_config=auto_detect,
                                        audio_config=audio_config())
result = recognizer.recognize_once_async().get()
detected = speechsdk.AutoDetectSourceLanguageResult(result).language
print(f"Detected language: {detected}\nText: {result.text}\n")

# 2. Phrase list: bias recognition towards domain words
recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,
                                        language="hi-IN" if not use_mic else "en-US",
                                        audio_config=audio_config())
phrase_list = speechsdk.PhraseListGrammar.from_recognizer(recognizer)
for phrase in ["Azure", "Foundry", "Deccansoft", "Voice Live"]:
    phrase_list.addPhrase(phrase)
result = recognizer.recognize_once_async().get()
print(f"With phrase list: {result.text}")
