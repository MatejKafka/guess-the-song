import subprocess
import sys
from pathlib import Path
from typing import List, Union
from .pyinstaller_util import find_executable

_FFPLAY_CMD = find_executable("ffplay")
_FFMPEG_CMD = find_executable("ffmpeg")


def _run_cmd(args: List, stdin_input: bytes = None, capture_stdout=False) -> subprocess.CompletedProcess:
	args = [str(arg) for arg in args]
	return subprocess.run(["cmd", "/c"] + args,
		input=stdin_input,
		stdout=subprocess.PIPE if capture_stdout else None,
		stderr=sys.stderr)


def play_segment(player_input: Union[Path, bytes], start_time: float = None, duration: float = None):
	"""
	Plays segment of `player_input` from `start_time`. Input can be provided either as file
		path or bytes object containing a valid audio file.
	"""
	# noinspection SpellCheckingInspection
	ffplay_args = ["-nostats", "-nodisp", "-autoexit", "-hide_banner"]

	if start_time is not None: ffplay_args += ["-ss", '%0.2f' % start_time]
	if duration is not None: ffplay_args += ["-t", '%0.2f' % duration]
	if type(player_input) is bytes:
		input_bytes = player_input
		player_input = "-"  # ffplay will read from stdin
	else:
		input_bytes = None
	result = _run_cmd([_FFPLAY_CMD, *ffplay_args, str(player_input)],
		stdin_input=input_bytes)

	if result.returncode != 0:
		raise Exception("Could not play segment - ffplay return exit code " + str(result.returncode))


def get_cropped_segment(file_path: Path, start_time: float = None, duration: float = None) -> bytes:
	"""
	Read input file from `file_path`, crop audio from `start_time`, `duration`
		seconds long and return output as bytes.
	"""

	# -vn = disable video (if present)
	# noinspection SpellCheckingInspection
	_FFMPEG_ARGS = ["-map_metadata", "-1", "-vn", "-acodec", "copy", "-hide_banner", "-loglevel", "panic", "-f", "mp3"]

	start_time_arg = ["-ss", '%0.2f' % start_time] if start_time is not None else []
	duration_arg = ["-t", '%0.2f' % duration] if duration is not None else []
	# -i <input> must be before some of the options in _FFMPEG_ARGS
	# "-" for output to stdout
	result = _run_cmd([_FFMPEG_CMD, "-i", str(file_path), *_FFMPEG_ARGS, *start_time_arg, *duration_arg, "-"],
		capture_stdout=True)

	if result.returncode != 0:
		raise Exception("Could not crop segment - ffmpeg returned exit code " + str(result.returncode))
	return result.stdout
