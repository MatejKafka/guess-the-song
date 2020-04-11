import json

from .lib.pyinstaller_util import CONFIG_PATH

with open(CONFIG_PATH, "r") as cfg_file:
	_cfg = json.load(cfg_file)
	MESSAGES = _cfg["messages"]
