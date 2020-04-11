import json

from .lib.pyinstaller_util import CONFIG_PATH

with open(CONFIG_PATH, "r") as cfg_file:
	_cfg = json.load(cfg_file)
	SERVER_HOST = _cfg["server"]["host"]
	SERVER_PORT = _cfg["server"]["port"]
	MESSAGES = _cfg["messages"]
