# Guess the song
Simple hacked-together project that allows multiple people
to connect to a server and play song segments synchronously
to all other connected clients.

**Sorry, the documentation is basically non-existent. If time allows,
I'd like to document this a bit more in the future. For now,
hopefully looking through the code should be enough to get you started.**

For now:
 - On windows, the server can be started by running run.ps1 in the server directory. It uses ngrok.exe to create a public https tunnel to localhost. Currently, port 12000 is used on localhost.
 - The ./client/build.ps1 script can be used to create a bundled single-file executable, internally it uses pyinstaller.
 - To run client directly from source, run `py launcher.py` in ./client directory.