from elevenlabs.client import ElevenLabs
from elevenlabs import play
from dotenv import load_env
import os

load_env()
ELEVENLABS_API_KEY = os.get_env("ELEVEN_LABS")

client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY
)

audio = client.text_to_speech.convert(
    text="The first move is what sets everything in motion.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
)

play(audio)
