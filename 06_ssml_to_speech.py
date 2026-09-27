"""Speech Synthesis Markup Language (SSML) to speech with two voices."""
import os
from xml.sax.saxutils import escape
from dotenv import load_dotenv
from playsound3 import playsound
import azure.cognitiveservices.speech as speechsdk

load_dotenv()
speech_key = os.environ["SPEECH_KEY"]
speech_endpoint = os.environ["SPEECH_ENDPOINT"]


def build_response_ssml(response_text: str) -> str:
    safe_text = escape(response_text)
    return f"""
<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
    <voice name='en-GB-LibbyNeural'>
        This is Voice in British Accent: {safe_text}
        <break strength='weak'/>
        I am from the United Kingdom. How are you doing today?
    </voice>
    <voice name='en-IN-PrabhatNeural'>
        This is Voice in Male Indian Accent: {safe_text}
        <break strength='weak'/>
        I am from India. How are you doing today?
    </voice>
</speak>
""".strip()


response_ssml = build_response_ssml("Welcome to the speech synthesis demo.")

speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=speech_endpoint)
speech_config.set_speech_synthesis_output_format(
    speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
)
audio_config = speechsdk.audio.AudioOutputConfig(filename="ssml_speech.mp3")
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

speak_result = speech_synthesizer.speak_ssml_async(response_ssml).get()

if speak_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech created successfully: ssml_speech.mp3")
    del speech_synthesizer  # close the file before playing
    playsound("ssml_speech.mp3")
elif speak_result.reason == speechsdk.ResultReason.Canceled:
    cancellation = speak_result.cancellation_details
    raise RuntimeError(
        f"Speech synthesis canceled: {cancellation.reason}; details: {cancellation.error_details}"
    )
