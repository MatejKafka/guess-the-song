import csv
import typing
import pathlib
import sys

from src.lib.ff import play_segment
from src.lib.sigint_handler import init_sigint_handler

CSV_NAME = "songs.csv"


class SongSegment(typing.NamedTuple):
	name: str
	path: pathlib.Path
	start_time: float
	comment: str

	def play(self, duration):
		play_segment(self.path, self.start_time, duration)


def iter_song_csv(folder_path):
	folder_path: pathlib.Path = pathlib.Path(folder_path).resolve()
	with (folder_path / CSV_NAME).open('r') as fd:
		for row in csv.reader(fd, skipinitialspace=True):
			(filename, start_time, comment) = row
			# noinspection PyDeepBugsBinOperator
			yield SongSegment(filename, folder_path / filename, float(start_time), comment)


if __name__ == "__main__":
	init_sigint_handler("Vypinam...")

	print("Napiste cestu ke slozce (napr. D:/guessing_game/Mates) s pisnickami.")
	print("Ve slozce by mel byt soubor songs.csv (viz slozka ./example),")
	print("na kazdem radku musi byt nazev souboru a cas, ve kterem se")
	print("ma pisnicka pustit, oddelene carkou.")
	print("")

	folder_path = input("Cesta ke slozce: ")

	for song in iter_song_csv(folder_path):
		print(f"\nPrehravam {song.name} od {song.start_time} vterin")

		while True:
			duration_str = input("Delka prehravani (nebo 'dalsi'): ")
			if duration_str.lower() in ["dalsi", "next", "n"]:
				break

			try:
				duration = float(duration_str)
			except ValueError:
				print("To nevypada jako cislo, ani jako neco z [dalsi, next, n], zkus to znovu...", file=sys.stderr)
				continue
			song.play(float(duration_str))

	input("\nCela slozka prehrana, zmackni <enter> pro ukonceni...")
