import asyncio
import time

import websockets

from src.lib.ff import play_segment
from ..CONFIG import SERVER_HOST, SERVER_PORT, MESSAGES


async def _run_receiver():
	server_url = "ws://" + SERVER_HOST + ":" + str(SERVER_PORT)
	print(f"Connecting to a server... ({server_url})")
	async with websockets.connect(server_url) as ws:
		await ws.send(MESSAGES["receiverSignature"])
		print("Connected")

		while True:
			# FIXME: this is not very robust
			print("Waiting for a song...")
			audio_track: bytes = await ws.recv()
			if type(audio_track) is not bytes:
				raise Exception("Expected to receive a song, received text data instead...")

			print("Song received, waiting for everyone else...")
			await ws.send(MESSAGES["songReceived"])
			await ws.recv()  # next message is confirmation
			print("Playing in 3...", end="")
			time.sleep(1)
			print("2...", end="")
			time.sleep(1)
			print("1...")
			time.sleep(1)
			print("Playing song...")
			play_segment(audio_track)
			print("Playback finished")


def __main__():
	asyncio.get_event_loop().run_until_complete(_run_receiver())


if __name__ == "__main__":
	__main__()
