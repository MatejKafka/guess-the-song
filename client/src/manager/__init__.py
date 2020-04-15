import sys

import websockets

from src.CONFIG import MESSAGES


async def __main__(ws: websockets.WebSocketClientProtocol):
	await ws.send(MESSAGES["managerSignature"])
	print("Connected")

	while True:
		user_input = input("Enter command (restart, force): ").lower()
		if user_input == "restart":
			await ws.send(MESSAGES["restartServer"])
			print("Sent restart request")
			print("Received response:", await ws.recv())
			print("Exiting...")
			sys.exit(0)
		elif user_input == "force":
			await ws.send(MESSAGES["triggerPlayback"])
			print("Force playback request sent")
			print("Received response:", await ws.recv())
		else:
			print("Invalid command, try again")
