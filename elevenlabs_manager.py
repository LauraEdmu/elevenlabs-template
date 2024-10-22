import os
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import asyncio
import aiofiles
import logging
import subprocess

# logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Configure logging to log to a file
# logger = logging.getLogger(__name__) # Create a logger

# console_handler = logging.StreamHandler() # Create a console handler
# console_handler.setLevel(logging.DEBUG)

# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Create a formatter and set it for the console handler
# console_handler.setFormatter(formatter)

# logger.addHandler(console_handler) # Add the console handler to the logger

class ElevenlabsManager:
	def __init__(self):
		self.logger = logging.getLogger(self.__class__.__name__)
		self.logger.setLevel(logging.DEBUG)
		
		# Create handlers if they aren't already set up
		if not self.logger.hasHandlers():
			console_handler = logging.StreamHandler()
			console_handler.setLevel(logging.DEBUG)
			file_handler = logging.FileHandler('ElevenlabsManager.log')
			file_handler.setLevel(logging.DEBUG)
			formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
			console_handler.setFormatter(formatter)
			file_handler.setFormatter(formatter)
			self.logger.addHandler(console_handler)
			self.logger.addHandler(file_handler)

		self.logger.debug("Initialised ElevenlabsManager instance")

	async def load_key(self, keypath="11.priv") -> bool:
		if not os.path.exists(keypath):
			self.logger.error("Key not found")
			return False

		async with aiofiles.open(keypath, "r") as key_file:
			api_key = await key_file.read()

		self.client = ElevenLabs(
			api_key=api_key,
		)

		self.logger.debug("Key read and assigned to client object")
		return True

	async def speak(self, msg: str, folder: str = "", voice_id: str = "nGBBtIZq3VIJ6mZdVhgY", stability: float = 0.5) -> str:
		if msg == "":
			self.logger.error("Message must not be empty")
			return ""

		# calling tts API
		response = await asyncio.to_thread(
			self.client.text_to_speech.convert,
			voice_id=voice_id,
			output_format="mp3_22050_32",
			text=msg,
			model_id="eleven_multilingual_v2",
			voice_settings=VoiceSettings(
				stability=stability,
				similarity_boost=1.0,
				style=0.0,
				use_speaker_boost=True,
			),
		)

		save_file_path = f"{uuid.uuid4()}.mp3"
		if folder != "":
			save_file_path_folder = os.path.join(folder, save_file_path)
		else:
			save_file_path_folder = save_file_path

		try:
			async with aiofiles.open(save_file_path_folder, "wb") as f:
				for chunk in response:
					if chunk:
						await f.write(chunk)

			self.logger.debug(f"{save_file_path_folder}: A new audio file was saved successfully!")
			return save_file_path_folder
		except FileNotFoundError as e:
			async with aiofiles.open(save_file_path, "wb") as f:
				for chunk in response:
					if chunk:
						await f.write(chunk)

			self.logger.error(f"{save_file_path}: A new audio file was saved successfully! NOTE: saved in script dir since {folder} wasn't found")
			return save_file_path

async def main():
	text = str(input("Enter Text: "))

	manager = ElevenlabsManager()

	if not await manager.load_key():
		return

	save_path = await manager.speak(text, folder="output")

if __name__ == '__main__':
	asyncio.run(main())