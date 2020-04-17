# slight hack - pyinstaller does not allow main file
#  as module, this file allows me to use module namespace
from src import __main__
if __name__ == "__main__":
	__main__()