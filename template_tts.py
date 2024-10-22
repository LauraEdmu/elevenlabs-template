import os
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import asyncio
import aiofiles
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Configure logging to log to a file
logger = logging.getLogger(__name__) # Create a logger

console_handler = logging.StreamHandler() # Create a console handler
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Create a formatter and set it for the console handler
console_handler.setFormatter(formatter)

logger.addHandler(console_handler) # Add the console handler to the logger

def text_to_speech_file(text: str, client: object) -> str:
	# Calling the text_to_speech conversion API with detailed parameters
	response = client.text_to_speech.convert(
		voice_id="jCm3i76UO6tBjwxdIoQV", # Adam pre-made voice
		output_format="mp3_22050_32",
		text=text,
		model_id="eleven_multilingual_v2", # use the turbo model for low latency
		voice_settings=VoiceSettings(
			stability=0.0,
			similarity_boost=1.0,
			style=0.0,
			use_speaker_boost=True,
		),
	)

	# uncomment the line below to play the audio back
	play(response)

	# Generating a unique file name for the output MP3 file
	save_file_path = f"{uuid.uuid4()}.mp3"

	# Writing the audio to a file
	save_file_path = os.path.join("output", save_file_path)
	with open(save_file_path, "wb") as f:
		for chunk in response:
			if chunk:
				f.write(chunk)

	print(f"{save_file_path}: A new audio file was saved successfully!")

	# Return the path of the saved audio file
	return save_file_path

async def main():
	try:
		async with aiofiles.open("11.priv", 'r') as f:
			ELEVENLABS_API_KEY = await f.read()
	except FileNotFoundError as e:
		logger.error(f"Key could not be found {e}")
		return

	client = ElevenLabs(
		api_key=ELEVENLABS_API_KEY,
	)

	text = str(input("Enter Text: "))

	logger.debug("Prompt recieved from user")
	
	save_path = await asyncio.to_thread(
		text_to_speech_file,
		text,
		client
	)

	logger.debug(f"Response from elevenlabs. Saved file path = {save_path}")

	# save_path = text_to_speech_file(text)

	print(f"Save Path: {save_path}")

if __name__ == '__main__':
	logger.debug("Entering __MAIN__")
	asyncio.run(main())