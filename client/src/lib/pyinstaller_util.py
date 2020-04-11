import os
import sys
import pathlib
import shutil
from typing import Union

# noinspection PyUnresolvedReferences
LAUNCHED_FROM_PYINSTALLER: bool = hasattr(sys, 'frozen') and sys.frozen and hasattr(sys, '_MEIPASS')
SCRIPT_DIR = pathlib.Path(__file__).parent.parent

if LAUNCHED_FROM_PYINSTALLER:
	CONFIG_PATH = SCRIPT_DIR / "../config.json"
else:
	CONFIG_PATH = SCRIPT_DIR / "../../config/config.json"


# noinspection PyUnusedFunction
def resolve_path(path: Union[str, pathlib.Path]) -> pathlib.Path:
	"""
	Resolves relative path to unpacked dir if running from pyinstaller package, or local path if running directly
	"""
	if type(path) == str:
		path = pathlib.Path(path)

	if LAUNCHED_FROM_PYINSTALLER:
		# noinspection PyProtectedMember,PyUnresolvedReferences
		return pathlib.Path(sys._MEIPASS) / path
	else:
		return SCRIPT_DIR / path


def find_executable(name: str):
	search_path = os.environ["PATH"]
	if LAUNCHED_FROM_PYINSTALLER:
		# prepend unpacked app path before PATH
		# noinspection PyProtectedMember,PyUnresolvedReferences
		search_path = sys._MEIPASS + os.pathsep + search_path
	return shutil.which(name, path=search_path)
