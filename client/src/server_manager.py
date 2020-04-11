import asyncio

import websockets

from .CONFIG import SERVER_HOST, SERVER_PORT, MESSAGES


async def _run_manager():
	server_url = "ws://" + SERVER_HOST + ":" + str(SERVER_PORT)
	print(f"Connecting to a server... ({server_url})")
	async with websockets.connect(server_url) as ws:
		await ws.send(MESSAGES["managerSignature"])
		print("Connected")

		while True:
			user_input = input("Enter command (restart, force): ").lower()
			if user_input == "restart":
				await ws.send(MESSAGES["restartServer"])
				print("Sent restart request")
				print("Received response:", await ws.recv())
				print("Exiting...")
				exit(0)
			elif user_input == "force":
				await ws.send(MESSAGES["triggerPlayback"])
				print("Force playback request sent")
				print("Received response:", await ws.recv())
			else:
				print("Invalid command, try again")


def __main__():
	asyncio.get_event_loop().run_until_complete(_run_manager())


if __name__ == "__main__":
	__main__()
