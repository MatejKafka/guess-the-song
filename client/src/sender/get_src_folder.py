import pathlib
from tkinter import Tk, filedialog

USE_GUI = True


async def get_src_folder() -> pathlib.Path:
	if not USE_GUI:
		return pathlib.Path(await ainput("Folder path: "))
	
	root = Tk()
	root.withdraw()
	songs_path = filedialog.askopenfilename(filetypes=[("songs.csv", "songs.csv")])
	root.destroy()
	return pathlib.Path(songs_path).parent
	