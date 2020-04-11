# slight hack - pyinstaller does not main file
#  as module, this allows me to use module namespace
from src import __main__
if __name__ == "__main__":
	__main__()