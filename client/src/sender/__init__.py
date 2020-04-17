from typing import NamedTuple, Optional, Awaitable, List, Callable, NoReturn
import pathlib
import csv

import websockets

from src.lib.ainput import ainput
from src.lib.ff import get_cropped_segment, play_segment
from src.CONFIG import MESSAGES
from .input_parser import Input, print_player_controls, get_user_input

CSV_NAME = "songs.csv"


class PresentableException(Exception):
	def __init__(self, msg: str):
		super().__init__(msg)


class SongSegment(NamedTuple):
	name: str
	path: pathlib.Path
	start_time: float
	comment: str

	def get_audio_track(self, duration):
		return get_cropped_segment(self.path, self.start_time, duration)


class Player:
	song_folder_path: Optional[str] = None
	songs: Optional[List[SongSegment]] = None
	sample_cb: Callable[[bytes], Awaitable[None]]

	def __init__(self, play_sample: Callable[[bytes], Awaitable[None]]):
		self.sample_cb = play_sample

	async def run(self):
		await self._get_songs()
		await self._run_player()

	@staticmethod
	def _parse_song_csv(folder_path) -> List[SongSegment]:
		folder_path: pathlib.Path = pathlib.Path(folder_path).resolve()

		if not folder_path.exists():
			raise PresentableException(f"Given folder does not exist ({folder_path})")

		try:
			fd = (folder_path / CSV_NAME).open('r')
		except FileNotFoundError as err:
			raise PresentableException(f"Given folder does not contain songs.csv ({folder_path / CSV_NAME})") from err
		except IOError as err:
			raise PresentableException(f"Could not read songs.csv ({folder_path / CSV_NAME})") from err

		with fd:
			songs = []
			for row in csv.reader(fd, skipinitialspace=True):
				(filename, start_time, comment) = row
				file_path = folder_path / filename
				if not file_path.exists():
					raise PresentableException(f"File from songs.csv does not exist ({folder_path / filename})")
				songs.append(SongSegment(filename, folder_path / filename, float(start_time), comment))

		return songs

	def _load_song_list(self, folder_path: str):
		try:
			self.songs = self._parse_song_csv(folder_path)
		except ValueError as err:
			raise PresentableException("songs.csv file exists, but it is incorrectly formatted") from err

		if len(self.songs) == 0:
			raise PresentableException("Song list exists, but it's empty")

	@staticmethod
	def _print_song_list_format():
		print("")
		print("Enter path to the song folder (e.g. D:/guessing_game/Mates).")
		print("The folder must contain a file called songs.csv (see the ./example folder),")
		print("with one or more lines in the format `file_name, playback_start_time, comment`")
		print("(3 values, separated by a comma). Playback time may be decimal.")
		print("")

	async def _get_songs(self):
		if self.song_folder_path is None:
			self._print_song_list_format()

		while True:
			folder_path = self.song_folder_path
			if folder_path is None:
				folder_path = await ainput("Folder path: ")

			try:
				self._load_song_list(folder_path)
				print(f"Song list successfully loaded ({len(self.songs)} songs)")
				self.song_folder_path = folder_path
				return
			except PresentableException as err:
				print(str(err))
			print("Please fix the issue and enter the folder path again")
			print("")

	async def _run_player(self):
		"""
		If true is returned, restart the player with reloaded song list.
		Otherwise exit.
		"""

		print_player_controls()

		song_i = 0
		while True:
			song = self.songs[song_i]
			print("Selected song:")
			print("    file name:", song.name)
			print("    start time:", song.start_time, "s")
			print("    comment:", song.comment)

			while True:
				itype, args = await get_user_input()

				if len(args) == 0:
					arg = None
				else:
					arg = args[0]

				if itype == Input.QUIT:
					return

				elif itype == Input.RELOAD:
					await self._get_songs()
					if song_i >= len(self.songs):
						print("Song list length changed, selected first song")
						song_i = 0
					break

				elif itype == Input.PREVIOUS:
					if song_i > 0:
						song_i -= 1
						print(f"Changed to song #{song_i+1} of {len(self.songs)}")
						break
					else:
						print("Already at the first song, cannot go to previous")

				elif itype == Input.NEXT:
					if song_i < len(self.songs) - 1:
						song_i += 1
						print(f"Changed to song #{song_i+1} of {len(self.songs)}")
						break
					else:
						print("Reached the end of song list")

				elif itype == Input.START_TIME:
					# tuples are immutable, have to copy
					# noinspection PyProtectedMember
					song = song._replace(start_time=arg)
					print("Changed playback start time to", arg, "(will be reset when changing song)")

				elif itype == Input.SET_SONG:
					# user will type in human offsets
					arg -= 1
					if arg < 0 or arg >= len(self.songs):
						print(f"Cannot select given song, there are only {len(self.songs)} songs loaded")
						continue
					song_i = arg
					print(f"Changed to song #{song_i+1} of {len(self.songs)}")
					break

				elif itype == Input.DURATION:
					print("Cropping the song sample...")
					track = await song.get_audio_track(arg)
					await self.sample_cb(track)

				else:
					raise Exception("Unhandled input type: " + str(itype))


async def __main__(ws: Optional[websockets.WebSocketClientProtocol]) -> NoReturn:
	"""
	:param ws: If param is None, offline mode will be used,
		otherwise will use provided connection for online mode.
	"""

	# setup Player
	if ws is None:
		# offline mode
		async def play_sample(track: bytes):
			print(f"Playing sample (size: {len(track)} bytes)")
			await play_segment(track)
			print("Sample played")
	else:
		# online mode
		await ws.send(MESSAGES["senderSignature"])
		print("Connected")

		async def play_sample(track: bytes):
			print(f"Sending the sample... (size: {len(track)} bytes)")
			await ws.send(track)
			print("Sample sent")
			await ws.recv()
			print("Confirmation received")

	player = Player(play_sample)
	await player.run()