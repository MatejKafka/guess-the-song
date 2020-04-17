import signal
import sys

EXIT_MESSAGE = None
MSG_STREAM = None
HANDLER_SET = False

# noinspection PyUnusedLocal
def _signal_handler(signal, frame):
	if EXIT_MESSAGE is not None:
		print("\n\n" + str(EXIT_MESSAGE), file=MSG_STREAM)
	sys.exit(0)


# noinspection PySameParameterValue
def init_sigint_handler(exit_message=None, output_stream=None):
	global EXIT_MESSAGE, HANDLER_SET, MSG_STREAM
	if not HANDLER_SET:
		HANDLER_SET = True
		EXIT_MESSAGE = exit_message
		MSG_STREAM = output_stream
		signal.signal(signal.SIGINT, _signal_handler)
	else:
		raise Exception("Tried to set SIGINT handler multiple times")