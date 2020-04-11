const WebSocket = require("ws")

const CONFIG = require("../config.json")
const PORT = process.env.PORT || CONFIG.devServer.port
const RECEIVER_SIGNATURE = CONFIG.messages.receiverSignature
const SENDER_SIGNATURE = CONFIG.messages.senderSignature
const MANAGER_SIGNATURE = CONFIG.messages.managerSignature


const handleHandshake = (ws, message) => {
	switch (message) {
		case RECEIVER_SIGNATURE:
			receivers.add(ws)
			console.log("new receiver connected")
			return true
		case SENDER_SIGNATURE:
			console.log("new sender connected")
			return true
		case MANAGER_SIGNATURE:
			console.log("manager connected")
			return true
		default:
			console.warn("First message from client is not signature, closing connection...")
			ws.close()
			return false
	}
}

const triggerReceiverPlayback = () => {
	console.log("triggering playback")
	for (const rec of receivers) {
		rec.send(CONFIG.messages.triggerPlayback)
	}
	confirmationCount = null
}

const broadcastSong = (audioTrack) => {
	if (receivers.size === 0) {
		console.warn("no receivers are connected, cannot broadcast song")
		return
	}
	console.log(`broadcasting song to ${receivers.size} receivers`)
	confirmationCount = 0
	for (const rec of receivers) {
		rec.send(audioTrack)
	}
}


// noinspection JSCheckFunctionSignatures
const wss = new WebSocket.Server({port: PORT}, () => {
	console.log("server running at port", PORT)
})

const receivers = new Set()
// null signifies no pending playback is waiting
let confirmationCount = null
let clientCount = 0

// noinspection JSUnresolvedFunction
wss.on("connection", function connection(ws) {
	let already_identified = false
	clientCount++

	console.log("someone is connecting...")

	ws.on("message", (message) => {
		if (!already_identified) {
			already_identified = handleHandshake(ws, message)
			return
		}

		if (message === CONFIG.messages.restartServer) {
			ws.send(CONFIG.messages.requestConfirmation)
			console.log("received restart request, exiting...")
			process.exit(0)
		}

		if (message === CONFIG.messages.triggerPlayback) {
			// playback can be forcefully triggered if necessary
			if (confirmationCount != null) {
				triggerReceiverPlayback()
				ws.send(CONFIG.messages.requestConfirmation)
			} else {
				console.warn("cannot force playback, no song is pending")
				ws.send(CONFIG.messages.requestError)
			}
			return
		}

		if (receivers.has(ws)) {
			if (message !== CONFIG.messages.songReceived) {
				console.warn("received something weird from a receiver... (message: " + message + ")")
				return
			}
			// this is a receiver sending confirmation
			confirmationCount++
			console.log(`received song confirmation (${confirmationCount}/${receivers.size})`)

			if (confirmationCount === receivers.size) {
				triggerReceiverPlayback()
			}
		} else {
			// this is a sender sending a song
			broadcastSong(message)
			ws.send(CONFIG.messages.songReceived)
		}
	})

	ws.on("close", () => {
		clientCount--
		receivers.delete(ws)
		console.log(`client disconnected (${clientCount} clients now connected)`)
	})
})