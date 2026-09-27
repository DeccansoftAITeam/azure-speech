"""Voice Live: real-time speech-to-speech conversation with a generative AI model.

    python 10_voice_live.py          # talk through the microphone (Ctrl+C to quit)
    python 10_voice_live.py --text "Tell me a joke"   # send text, hear the spoken reply

Voice Live is fully managed: STT + LLM + TTS in one WebSocket session, with noise suppression,
echo cancellation, semantic end-of-turn detection, barge-in (interruption) and Azure neural voices.
"""
import asyncio
import base64
import os
import sys
import wave

import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    AudioEchoCancellation,
    AudioInputTranscriptionOptions,
    AudioNoiseReduction,
    AzureSemanticVad,
    AzureStandardVoice,
    InputAudioFormat,
    InputTextContentPart,
    Modality,
    OutputAudioFormat,
    RequestSession,
    ServerEventType,
    UserMessageItem,
)

load_dotenv()
ENDPOINT = os.environ["SPEECH_ENDPOINT"]
API_KEY = os.environ["SPEECH_KEY"]
MODEL = os.getenv("VOICE_LIVE_MODEL", "gpt-realtime-mini")
SAMPLE_RATE = 24000  # PCM16, 24 kHz, mono


async def run(text_prompt=None):
    async with connect(endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY), model=MODEL) as conn:
        # Configure the session: instructions, voice, audio formats, turn detection
        session = RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            instructions="You are a friendly AI teacher. Keep answers short and conversational.",
            voice=AzureStandardVoice(name="en-US-AvaMultilingualNeural"),
            input_audio_format=InputAudioFormat.PCM16,
            output_audio_format=OutputAudioFormat.PCM16,
            input_audio_transcription=AudioInputTranscriptionOptions(model="azure-speech"),
            input_audio_noise_reduction=AudioNoiseReduction(type="azure_deep_noise_suppression"),
            input_audio_echo_cancellation=AudioEchoCancellation(),
            turn_detection=AzureSemanticVad(),
        )
        await conn.session.update(session=session)

        speaker = sd.OutputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16")
        speaker.start()
        reply_audio = bytearray()
        loop = asyncio.get_running_loop()

        if text_prompt:
            # Text in, speech out
            print(f"You: {text_prompt}")
            await conn.conversation.item.create(
                item=UserMessageItem(content=[InputTextContentPart(text=text_prompt)])
            )
            await conn.response.create()
        else:
            # Stream microphone audio to the service
            def on_mic(indata, frames, time_info, status):
                audio_b64 = base64.b64encode(indata.tobytes()).decode()
                asyncio.run_coroutine_threadsafe(conn.input_audio_buffer.append(audio=audio_b64), loop)

            mic = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                                 blocksize=SAMPLE_RATE // 20, callback=on_mic)
            mic.start()
            print("Listening... speak now (Ctrl+C to quit)")

        async for event in conn:
            if event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
                print("[you are speaking...]")
                speaker.abort(); speaker.start()  # barge-in: stop the assistant talking
            elif event.type == ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED:
                print(f"You: {event.transcript}")
            elif event.type == ServerEventType.RESPONSE_AUDIO_DELTA:
                reply_audio.extend(event.delta)
                speaker.write(np.frombuffer(event.delta, dtype=np.int16))
            elif event.type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE:
                print(f"Assistant: {event.transcript}")
            elif event.type == ServerEventType.ERROR:
                print(f"Error: {event.error.message}")
            elif event.type == ServerEventType.RESPONSE_DONE and text_prompt:
                break

        speaker.stop()
        if text_prompt:
            with wave.open("voice_live_reply.wav", "wb") as f:
                f.setnchannels(1); f.setsampwidth(2); f.setframerate(SAMPLE_RATE)
                f.writeframes(bytes(reply_audio))
            print(f"Saved voice_live_reply.wav ({len(reply_audio)} bytes)")


if __name__ == "__main__":
    prompt = sys.argv[sys.argv.index("--text") + 1] if "--text" in sys.argv else None
    try:
        asyncio.run(run(prompt))
    except KeyboardInterrupt:
        print("\nBye!")
