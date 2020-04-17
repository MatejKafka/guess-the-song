import logging
from datetime import datetime
import os
import traceback


def setup_logging():
	try:
		os.makedirs("./logs")
	except FileExistsError:
		pass

	log_file = "./logs/" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f") + ".log"

	logging.basicConfig(
		level=logging.DEBUG,
		filename=log_file)


def log_exception(err: Exception):
	if isinstance(err, SystemExit):
		return

	try:
		os.makedirs("./logs")
	except FileExistsError:
		pass

	# if a terminating error occurs, log it
	with open("./logs/_error.log", "w") as fd:
		fd.write(traceback.format_exc())