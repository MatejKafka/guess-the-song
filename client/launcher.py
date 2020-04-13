# slight hack - pyinstaller does not main file
#  as module, this file allows me to use module namespace
from src import __main__
if __name__ == "__main__":
	# noinspection PyBroadException
	try:
		__main__()
	except Exception as err:
		if not isinstance(err, SystemExit):
			# if a terminating error occurs, log it
			import traceback
			with open("./error.log", "w") as fd:
				fd.write(traceback.format_exc())
			raise