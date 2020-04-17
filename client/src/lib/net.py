from __future__ import annotations
import secrets
from contextlib import asynccontextmanager
from typing import Union, Iterable, AsyncIterable, Optional

import websockets


# TODO: implement server counterpart and actually use this
class ServerConnection:
	_WS = websockets.WebSocketClientProtocol
	Data = websockets.Data
	SendData = Union[Data, Iterable[Data], AsyncIterable[Data]]

	# noinspection SpellCheckingInspection
	_PROTOCOL_SIGNATURE = b"guessthesong"

	connection_id: bytes

	@staticmethod
	@asynccontextmanager
	async def connect(server_url: str) -> ServerConnection:
		conn = ServerConnection(server_url)
		await conn._connect()
		yield conn
		await conn.close()

	def __init__(self, server_url: str):
		self._server_url = server_url
		self._conn_id = secrets.token_bytes(4)
		self._conn: Optional[ServerConnection._WS] = None

	async def _connect(self):
		try:
			# disable max limit on message size to allow sending large songs
			# noinspection PyTypeChecker
			self._conn = await websockets.connect(self._server_url, max_size=None)
			await self._conn.send(ServerConnection._PROTOCOL_SIGNATURE + self._conn_id)
			response = await self._conn.recv()
		except websockets.WebSocketException as err:
			raise ConnectionError("Error occurred while initializing server connection") from err

		if type(response) != bytes:
			raise ConnectionError("Server handshake should be binary, received text instead")
		if len(response) != 8 or response[0:4] != ServerConnection._PROTOCOL_SIGNATURE:
			raise ConnectionError("Invalid server handshake response: " + response.decode("utf8", errors="ignore"))
		if response[4:8] != self._conn_id:
			raise ConnectionError("Connection ID returned from server does not match sent client ID")

	async def _reconnect_wrapper(self, fn):
		if self._conn is None:
			raise Exception("Not connected")
		while True:
			try:
				return await fn()
			except websockets.WebSocketException:
				# TODO: change into error callback, printing from random places is not nice
				print("Connection lost while sending data, reconnecting...")
				await self._connect()
				print("Reconnected")


	async def send(self, data: SendData):
		async def fn():
			await self._conn.send(data)
		await self._reconnect_wrapper(fn)

	async def recv(self):
		async def fn():
			await self._conn.recv()
		await self._reconnect_wrapper(fn)

	async def close(self):
		if self._conn is None:
			raise Exception("Not connected")
		await self._conn.close()