from typing import NamedTuple, Optional, Awaitable, List, Tuple, Callable, NoReturn
import pathlib
import csv
import enum

import websockets

from src.lib.ainput import ainput
from src.lib.ff import get_cropped_segment, play_segment
from src.CONFIG import MESSAGES

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


@enum.unique
class UserPlayerInput(enum.Enum):
	QUIT = enum.auto()
	RELOAD = enum.auto()
	NEXT = enum.auto()
	PREVIOUS = enum.auto()
	DURATION = enum.auto()
	START_TIME = enum.auto()


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

	@staticmethod
	def print_player_controls():
		print("Playback control:")
		print("    <decimal_number> -> play n seconds of song")
		print("    n/next -> skip to next song")
		print("    p/prev/previous -> return to previous song")
		print("    s/start <decimal_number> -> change playback start time")
		print("    q/quit -> quit the program")
		print("    r/reload -> reload current song list")
		print("")

	@staticmethod
	async def _get_user_input() -> Tuple[UserPlayerInput, Optional[float]]:
		print("")
		user_input = (await ainput("Input: ")).lower()
		if user_input in ["n", "next"]:
			return UserPlayerInput.NEXT, None
		if user_input in ["p", "prev", "previous"]:
			return UserPlayerInput.PREVIOUS, None
		if user_input in ["q", "quit"]:
			return UserPlayerInput.QUIT, None
		if user_input in ["r", "reload"]:
			return UserPlayerInput.RELOAD, None
		if user_input.startswith("s ") or user_input.startswith("start "):
			_, user_input = user_input.split()
			ret = UserPlayerInput.START_TIME
		else:
			ret = UserPlayerInput.DURATION
		try:
			return ret, float(user_input)
		except ValueError:
			print("Incorrect input, try again")
			Player.print_player_controls()
			return await Player._get_user_input()


	async def _run_player(self):
		"""
		If true is returned, restart the player with reloaded song list.
		Otherwise exit.
		"""

		self.print_player_controls()

		song_i = 0
		while True:
			song = self.songs[song_i]
			print("Selected song:")
			print("    file name:", song.name)
			print("    start time:", song.start_time, "s")
			print("    comment:", song.comment)

			while True:
				itype, user_input = await self._get_user_input()

				if itype == UserPlayerInput.QUIT:
					return
				elif itype == UserPlayerInput.RELOAD:
					await self._get_songs()
					if song_i >= len(self.songs):
						print("Song list length changed, selected first song")
						song_i = 0
					break
				elif itype == UserPlayerInput.PREVIOUS:
					if song_i > 0:
						song_i -= 1
						print(f"Changed to song #{song_i+1} of {len(self.songs)}")
						break
					else:
						print("Already at the first song, cannot go to previous")
				elif itype == UserPlayerInput.NEXT:
					if song_i < len(self.songs) - 1:
						song_i += 1
						print(f"Changed to song #{song_i+1} of {len(self.songs)}")
						break
					else:
						print("Reached the end of song list")
				elif itype == UserPlayerInput.START_TIME:
					# tuples are immutable, have to copy
					# noinspection PyProtectedMember
					song = song._replace(start_time=user_input)
					print("Changed playback start time to", user_input, "(will be reset when changing song)")
				elif itype == UserPlayerInput.DURATION:
					print("Cropping the song sample...")
					track = await song.get_audio_track(user_input)
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
		print("")

		async def play_sample(track: bytes):
			print(f"Sending the sample... (size: {len(track)} bytes)")
			await ws.send(track)
			print("Sample sent")
			await ws.recv()
			print("Confirmation received")

	player = Player(play_sample)
	await player.run()