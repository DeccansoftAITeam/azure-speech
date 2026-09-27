"""Azure AI Speech SDK: Text to Speech (SpeechSynthesizer) and Speech to Text (SpeechRecognizer)."""
import os
from dotenv import load_dotenv
from playsound3 import playsound
import azure.cognitiveservices.speech as speech_sdk


def main():
    load_dotenv()

    # Create speech_config using key-based authentication
    speech_config = speech_sdk.SpeechConfig(
        subscription=os.environ["SPEECH_KEY"],
        endpoint=os.environ["SPEECH_ENDPOINT"],
    )

    # Loop until user quits
    inputText = ""
    while inputText != "3":
        inputText = input("Choose an option:\n1: Text to Speech\n2: Speech to Text (microphone)\n"
                          "3: Exit\n4: Speech to Text (voice.wav file)\n").strip()
        if inputText == "1":
            TextToSpeech(speech_config)
        elif inputText == "2":
            SpeechToText(speech_config, use_mic=True)
        elif inputText == "4":
            SpeechToText(speech_config, use_mic=False)
        elif inputText == "3":
            print("Exiting...")
        else:
            print("Invalid option, please try again.")


# TextToSpeech function (Create Audio file)
def TextToSpeech(speech_config):
    print("Recording greeting...")
    greeting_message = "Hi, Adam here. Are you still on for coffee this afternoon?"

    # Synthesize the greeting message to an audio file
    output_file = "voice.wav"
    audio_output_config = speech_sdk.audio.AudioOutputConfig(filename=output_file)
    # speech_config.speech_synthesis_voice_name = "en-US-Ava:DragonHDLatestNeural"
    # speech_config.set_speech_synthesis_output_format(speech_sdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
    speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"  # or "en-GB-ThomasNeural"
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)

    result = speech_synthesizer.speak_text_async(greeting_message).get()
    if result.reason == speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Greeting recorded and saved to {output_file}")
        del speech_synthesizer  # Release the synthesizer so the file is closed
        print("Playing sound...")
        playsound(output_file)
    else:
        print("Error recording greeting: {}".format(result.reason))
        if result.reason == speech_sdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            print("Cancellation reason: {}".format(cancellation.reason))
            print("Error details: {}".format(cancellation.error_details))


# Speech to Text: from the microphone or from voice.wav
def SpeechToText(speech_config, use_mic=True):
    if use_mic:
        print("Listening for speech input...")
        audio_config = speech_sdk.audio.AudioConfig(use_default_microphone=True)
    else:
        file_name = "voice.wav"
        print(f"\nTranscribing {file_name}...")
        audio_config = speech_sdk.audio.AudioConfig(filename=file_name)

    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    result = speech_recognizer.recognize_once_async().get()
    if result.reason == speech_sdk.ResultReason.RecognizedSpeech:
        print(f"Transcription: {result.text}")
    else:
        print("Error transcribing message: {}".format(result.reason))


if __name__ == "__main__":
    main()
