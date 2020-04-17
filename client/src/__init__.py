# called before importing other modules
# we have to configure logging before modules initialize their loggers
from .setup_logging import setup_logging, log_exception
setup_logging()

import asyncio

import websockets

from .lib.sigint_handler import init_sigint_handler
from .lib.ainput import ainput
from .receiver import __main__ as run_receiver
from .sender import __main__ as run_sender
from .manager import __main__ as run_manager


async def _run_online(mode: str):
	server_url = await ainput("Enter server URL: ")

	if not server_url.startswith("wss://") and not server_url.startswith("ws://"):
		if server_url.startswith("localhost"):
			server_url = "ws://" + server_url
		else:
			server_url = "wss://" + server_url
		print("URL corrected to " + server_url)

	print("Connecting...")

	try:
		# disable max limit on message size to allow sending large songs
		# noinspection PyTypeChecker
		async with websockets.connect(server_url, max_size=None) as ws:
			if mode == "2":
				print("Starting a receiver...")
				await run_receiver(ws)
			elif mode == "3":
				print("Starting a sender...")
				await run_sender(ws)
			else:
				print("Starting a debug manager...")
				await run_manager(ws)
	except websockets.InvalidURI:
		print("The URL you entered is not valid, please try again")
		await _run_online(mode)


async def _run_client():
	init_sigint_handler("Quitting...")

	while True:
		mode = await ainput("Select mode (1=offline, 2=receiver, 3=sender, 4=debug): ")
		mode = mode.strip()
		if mode in ("1", "2", "3", "4"): break
		print("Invalid input, try again...")

	if mode == "1":
		print("Starting in offline mode...")
		await run_sender(None)
	else:
		await _run_online(mode)

	print("")
	print("Quitting...")


def __main__():
	try:
		loop = asyncio.get_event_loop()
		loop.run_until_complete(_run_client())
	except Exception as err:
		log_exception(err)
		raise
