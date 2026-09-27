"""Translate text with Azure Translator, then transliterate the Hindi output to Latin script."""
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.translation.text import TextTranslationClient

load_dotenv()
foundry_endpoint = os.environ["SPEECH_ENDPOINT"].rstrip("/")
client = TextTranslationClient(endpoint=foundry_endpoint, credential=DefaultAzureCredential())
targetLanguage = "hi"

# Translate text
inputText = input("Enter text to translate: ")
translationResponse = client.translate(body=[inputText], to_language=[targetLanguage])
translation = translationResponse[0]
sourceLanguage = translation.detected_language

for translated_text in translation.translations:
    print(f"'{inputText}' was translated from {sourceLanguage.language} to {translated_text.to} "
          f"as '{translated_text.text}'.")

    # Transliterate the translated text to Latin script
    transliterationResponse = client.transliterate(
        body=[translated_text.text],
        language=translated_text.to,
        from_script="Deva",  # Devanagari (used by Hindi)
        to_script="Latn",    # Latin (romanized)
    )
    if transliterationResponse and transliterationResponse[0]:
        print(f"Transliteration: '{transliterationResponse[0].text}'")
