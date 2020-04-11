import asyncio

import websockets

from .lib.sigint_handler import init_sigint_handler
from .receiver import __main__ as run_receiver
from .sender import __main__ as run_sender
from .manager import __main__ as run_manager


async def _run_client():
	init_sigint_handler("Quitting...")

	server_url = input("Enter server URL: ")
	print(f"Connecting to a server... ({server_url})")
	async with websockets.connect(server_url) as ws:
		while True:
			mode = input("Select mode (1=receiver, 2=sender): ")
			if mode.strip() in ("1", "2", "3"): break
			print("Invalid input, try again...")

		if mode == "1":
			print("Starting a receiver...")
			await run_receiver(ws)
		elif mode == "2":
			print("Starting a sender...")
			await run_sender(ws)
		else:
			print("Starting a manager...")
			await run_manager(ws)


def __main__():
	asyncio.get_event_loop().run_until_complete(_run_client())


if __name__ == "__main__":
	__main__()