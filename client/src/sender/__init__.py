import typing
import pathlib
import csv
import enum

import websockets

from src.lib.ff import get_cropped_segment
from ..CONFIG import MESSAGES

CSV_NAME = "songs.csv"


class SongSegment(typing.NamedTuple):
	name: str
	path: pathlib.Path
	start_time: float
	comment: str

	def get_audio_track(self, duration):
		return get_cropped_segment(self.path, self.start_time, duration)


def _parse_song_csv(folder_path) -> typing.List[SongSegment]:
	folder_path: pathlib.Path = pathlib.Path(folder_path).resolve()
	with (folder_path / CSV_NAME).open('r') as fd:
		songs = []
		for row in csv.reader(fd, skipinitialspace=True):
			(filename, start_time, comment) = row
			songs.append(SongSegment(filename, folder_path / filename, float(start_time), comment))
	return songs


def _get_songs() -> typing.List[SongSegment]:
	print("Enter path to the song folder (e.g. D:/guessing_game/Mates).")
	print("The folder must contain a file called songs.csv (see the ./example folder),")
	print("with one or more lines in the format `file_name, playback_start_time, comment`")
	print("(3 values, separated by a comma). Playback time may be decimal.")
	print("")

	while True:
		folder_path = input("Folder path: ")

		try:
			songs = _parse_song_csv(folder_path)
			print(f"Song list successfully loaded ({len(songs)} songs)")
			return songs
		except FileNotFoundError:
			print("Entered folder does not contain songs.csv file, please try again")
		except ValueError:
			print("songs.csv file exists, but it is incorrectly formatted")
			print("Please fix the file and enter the folder path again")


def print_player_controls():
	print("Playback control:")
	print("    <decimal_number> -> play n seconds of song")
	print("    n/next -> skip to next song")
	print("    p/prev/previous -> return to previous song")
	print("    s/start <decimal_number> -> change playback start time")
	print("    q/quit -> quit the program")


@enum.unique
class UserPlayerInput(enum.Enum):
	NEXT = enum.auto()
	PREVIOUS = enum.auto()
	DURATION = enum.auto()
	START_TIME = enum.auto()


def _get_user_input() -> typing.Tuple[UserPlayerInput, typing.Optional[float]]:
	user_input = input("Input: ").lower()
	if user_input in ["n", "next"]:
		return UserPlayerInput.NEXT, None
	if user_input in ["p", "prev", "previous"]:
		return UserPlayerInput.PREVIOUS, None
	if user_input in ["q", "quit"]:
		print("")
		print("Quitting...")
		print("")
		exit(0)
	if user_input.startswith("s ") or user_input.startswith("start "):
		_, user_input = user_input.split()
		ret = UserPlayerInput.START_TIME
	else:
		ret = UserPlayerInput.DURATION
	try:
		return ret, float(user_input)
	except ValueError:
		print("Incorrect input, try again")
		print_player_controls()
		return _get_user_input()


async def _run_player(songs: typing.List[SongSegment],
			sample_cb: typing.Callable[[bytes], typing.Awaitable[None]]):
	print_player_controls()

	song_i = 0
	while True:
		song = songs[song_i]
		print("")
		print("Selected song:")
		print("    file name:", song.name)
		print("    start time:", song.start_time, "s")
		print("    comment:", song.comment)

		while True:
			itype, user_input = _get_user_input()

			if itype == UserPlayerInput.PREVIOUS:
				if song_i > 0:
					song_i -= 1
					print(f"Changed to song #{song_i+1} of {len(songs)}")
					break
				else:
					print("Already at the first song, cannot go to previous")
			elif itype == UserPlayerInput.NEXT:
				if song_i < len(songs) - 1:
					song_i += 1
					print(f"Changed to song #{song_i+1} of {len(songs)}")
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
				track = song.get_audio_track(user_input)
				print("Sending the sample...")
				await sample_cb(track)
			else:
				raise Exception("Unhandled input type: " + str(itype))


async def __main__(ws: websockets.WebSocketClientProtocol):
	await ws.send(MESSAGES["senderSignature"])
	print("Connected")
	print("")
	songs = _get_songs()
	print("")

	if len(songs) == 0:
		raise Exception("Song list is empty")

	async def play_sample(track: bytes):
		await ws.send(track)
		print("Sample sent")
		await ws.recv()
		print("Confirmation received")

	await _run_player(songs, play_sample)