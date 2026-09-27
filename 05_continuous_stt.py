"""Continuous Speech to Text from the microphone."""
import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv(override=True)

# Set up the speech config using resource endpoint
speech_config = speechsdk.SpeechConfig(
    subscription=os.environ["SPEECH_KEY"],
    endpoint=os.environ["SPEECH_ENDPOINT"],
)

# Create a recognizer with microphone input
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)


# Event handlers
def recognized_handler(evt):
    print(f"Recognized: {evt.result.text}")


def recognizing_handler(evt):
    print(f"Recognizing: {evt.result.text}")


# Connect event handlers
speech_recognizer.recognized.connect(recognized_handler)
speech_recognizer.recognizing.connect(recognizing_handler)

# Start continuous recognition
speech_recognizer.start_continuous_recognition()
print("Say something...")

# Keep the program running
input("Press Enter to stop...\n")
speech_recognizer.stop_continuous_recognition()
