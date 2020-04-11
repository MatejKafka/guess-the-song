from .lib.sigint_handler import init_sigint_handler
from .receiver import __main__ as run_receiver
from .sender import __main__ as run_sender


def __main__():
	init_sigint_handler("Quitting...")

	while True:
		mode = input("Select mode (1=receiver, 2=sender): ")
		if mode.strip() in ("1", "2"): break
		print("Invalid input, try again...")

	if mode == "1":
		print("Starting a receiver...")
		run_receiver()
	else:
		print("Starting a sender...")
		run_sender()


if __name__ == "__main__":
	__main__()
