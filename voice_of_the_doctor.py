# if you dont use pipenv uncomment the following:
# from dotenv import load_dotenv
# load_dotenv()

import os
from gtts import gTTS
import elevenlabs
from elevenlabs.client import ElevenLabs
import subprocess
import platform

ELEVENLABS_API_KEY=os.environ.get("ELEVEN_API_KEY")

# --- NEW FUNCTION FOR FASTAPI ---
def text_to_speech_with_elevenlabs_api(input_text: str, api_key: str) -> bytes:
    """
    Generates speech from text using the ElevenLabs API and returns the audio as bytes.
    This is suitable for use in a backend API where you send the audio data to a client.
    """
    client = ElevenLabs(api_key=api_key)
    try:
        # Generate the audio stream from the text
        audio_stream = client.generate(
            text=input_text,
            voice="Aria",
            output_format="mp3_22050_32",
            model="eleven_turbo_v2"
        )
        # The stream is an iterator of byte chunks; concatenate them into a single bytes object
        audio_bytes = b"".join(chunk for chunk in audio_stream)
        return audio_bytes
    except Exception as e:
        print(f"An error occurred with the ElevenLabs API: {e}")
        raise

# --- EXISTING FUNCTIONS (can be kept for other uses or removed if no longer needed) ---

def text_to_speech_with_gtts(input_text, output_filepath):
    language="en"
    audioobj = gTTS(text=input_text, lang=language, slow=False)
    audioobj.save(output_filepath)
    # Note: The subprocess calls below will only work when running on a desktop, not a server.
    # It's better to handle audio playback on the client-side.
    print(f"Audio saved to {output_filepath}")


def text_to_speech_with_elevenlabs(input_text, output_filepath):
    """
    Generates speech and saves it to a file, without attempting to play it.
    """
    client=ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio=client.generate(
        text= input_text,
        voice= "Aria",
        output_format= "mp3_22050_32",
        model= "eleven_turbo_v2"
    )
    elevenlabs.save(audio, output_filepath)
    print(f"Audio saved to {output_filepath}")