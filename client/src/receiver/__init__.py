import time

import websockets

from src.lib.ff import play_segment
from ..CONFIG import MESSAGES


async def __main__(ws: websockets.WebSocketClientProtocol):
	await ws.send(MESSAGES["receiverSignature"])
	print("Connected")

	while True:
		# FIXME: this is not very robust
		print("Waiting for a song...")
		audio_track: bytes = await ws.recv()
		if type(audio_track) is not bytes:
			raise Exception("Expected to receive a song, received " +
				f"text data instead... (msg: {audio_track})")

		print("Song received, waiting for everyone else...")
		await ws.send(MESSAGES["songReceived"])
		await ws.recv()  # next message is confirmation
		print("Playing in 3...", end="", flush=True)
		time.sleep(0.3)
		print("2...", end="", flush=True)
		time.sleep(0.3)
		print("1...", end="", flush=True)
		time.sleep(0.3)
		print("now")
		await play_segment(audio_track)
		print("Playback finished")
		print("")