import enum
from typing import Tuple

from src.lib.ainput import ainput
from .lib.command_parser import CommandParser


@enum.unique
class Input(enum.Enum):
	QUIT = enum.auto()
	RELOAD = enum.auto()
	NEXT = enum.auto()
	PREVIOUS = enum.auto()
	DURATION = enum.auto()
	START_TIME = enum.auto()
	SET_SONG = enum.auto()


def print_player_controls():
	print("Playback control:")
	print("    <decimal_number> -> play n seconds of song")
	print("    n/next -> skip to next song")
	print("    p/prev/previous -> return to previous song")
	print("    s/start <decimal_number> -> change playback start time")
	print("    i <integer_number> -> change to nth song")
	print("    q/quit -> quit the program")
	print("    r/reload -> reload current song list")


parser = CommandParser((Input.DURATION, float), [
	(Input.NEXT, ["n", "next"]),
	(Input.PREVIOUS, ["p", "prev", "previous"]),
	(Input.QUIT, ["q", "quit"]),
	(Input.RELOAD, ["r", "reload"]),

	(Input.START_TIME, ["s", "start"], float),
	(Input.SET_SONG, ["i"], int)
])


async def get_user_input() -> Tuple[Input, Tuple]:
	while True:
		print("")
		user_input = (await ainput("Input: ")).lower()

		try:
			return parser.parse(user_input)
		except ValueError:
			pass

		print("Incorrect input, try again")
		print_player_controls()
