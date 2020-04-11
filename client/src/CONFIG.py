import json
import os

from .lib.pyinstaller_util import CONFIG_PATH

with open(CONFIG_PATH, "r") as cfg_file:
	_cfg = json.load(cfg_file)
	if not "DEV" in os.environ:
		SERVER_HOST = _cfg["prodServer"]["host"]
		SERVER_PORT = _cfg["prodServer"]["port"]
	else:
		SERVER_HOST = _cfg["devServer"]["host"]
		SERVER_PORT = _cfg["devServer"]["port"]
	MESSAGES = _cfg["messages"]
