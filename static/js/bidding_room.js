const BidderState = {
	WAITING: 1,
	BIDDING: 2,
	ENDED: 3
}

var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port + '/room')

var playerBox = $("#player-box")
var bidBox = $("#bid-box")
var bidStateBox = $("#bid-state-box")
var statusBox = $("#status-box")
var bidTarget = $("#bid-target")

var btnBidIncrement = $("#bid-increment")
var btnBidDecrement = $("#bid-decrement")
var btnStart = $("#button-start")
var btnJoin = $("#button-join")
var btnLeave = $("#button-leave")
var bidAmount = $("#bid-amount")

var currentBidValue = 0
var currentBidTarget = null
var currentPlayer = null

btnBidDecrement.click(() => {
	currentBidValue = Math.max(0, currentBidValue - 1)
	refreshBidValue()
})

btnBidIncrement.click(() => {
	currentBidValue = Math.min(99, currentBidValue + 1)
	refreshBidValue()
})

bidAmount.change((event) => {
	currentBidValue = Math.max(0, Math.min(99, parseInt($(event.target).val())))
	refreshBidValue()
})

function resetBidStatus(){
	currentBidValue = 0
	currentBidTarget = null

	refreshBidValue()
	refreshBidTarget()
}

function refreshBidValue(){
	bidAmount.val(currentBidValue)
}

function refreshBidTarget(){
	if(!currentBidTarget){
		bidTarget.text("")
		return
	}

	bidTarget.text("Bidding on " + formatCombination(currentBidTarget))
	bidAmount.val(currentBidValue)
}

socket.on('connect', function() {
	socket.emit('enter', {roomId: roomId, player: username})

	if(roomOwner === username){
		socket.emit('join', {roomId: roomId, player: username})
	}
})

// socket.on('connect', function() {
// 	socket.emit('join', {roomId: roomId, player: username})
// })
socket.on('players', function(msg) {
	playerBox.empty()
	msg.players.forEach((player) => {
		let entry = $("<li/>").addClass("list-group-item")
		entry.html(player)
		playerBox.append(entry)
	})
})
socket.on('state', function(msg) {
	handleState(msg.state)
})
socket.on('close', function(msg) {
	document.location = '/'
})

function formatCombination(combination){
	return combination.join("-")
}

function targetCombination(combination, bidValue){
	currentBidTarget = combination
	currentBidValue = bidValue

	for(const k in combinationEntries){
		combinationEntries[k].removeClass("active")
	}
	combinationEntries[formatCombination(combination)].addClass("active")

	refreshBidTarget()
	refreshBidValue()
}

var combinationEntries = {}
function handleState(state){
	bidStateBox.empty()
	resetBidStatus()

	// Start/Join button
	if(roomOwner === username){
		btnJoin.hide()
		if(state.state === BidderState.WAITING){
			btnStart.show()
		}else{
			btnStart.hide()
		}
	}else{
		if(state.players.indexOf(username) >= 0){
			btnJoin.hide()
		}else{
			btnJoin.show()
		}

		btnStart.hide()
	}

	combinationEntries = {}
	const factionToBids = {}

	// List players
	playerBox.empty()
	state.players.forEach((player) => {
		let entry = $("<div/>").addClass("text-center p-4 player-item")
		entry.html(player)
		playerBox.append(entry)
	})

	// Convert bids
	for(const k in state.bids){
		var bid = state.bids[k]
		factionToBids[formatCombination(bid[0])] = [k, bid[1]]
	}

	// List combinations and bids
	var combinations = state.combinations
	for (let i = 0; i < combinations.length; i++) {
		let combination = combinations[i]
		let combinationStr = formatCombination(combination)
		let bid = factionToBids[combinationStr]

		let combinationStatus = combinationStr + (bid ? " => " + bid[0] + " for $" + bid[1]: "")
		let entry = $("<div/>")
			.addClass("row")
			.addClass("bidding-entry")
			.addClass("text-center")
			.addClass("align-middle")

		let button =
			$("<button/>")
				.addClass("btn btn-dark")
				.html("Bid")
				.click(
					() => {
						bidBox.show()
						targetCombination(combination, bid ? bid[1] + 1 : 0)
					}
				)
		let buttonDiv = $("<div/>")
			.addClass("col-2")
			.append(button)

		let bidder = bid ? bid[0] : ""
		let bidAmount = bid ? "$" + bid[1] : ""
		entry
			.append(buttonDiv)
			.append($("<div/>").addClass("col h6").html(combinationStr))
			.append($("<div/>").addClass("col").html(bidder))
			.append($("<div/>").addClass("col").html(bidAmount))
		combinationEntries[combinationStr] = entry

		bidStateBox.append(entry)
	}

	// Display current state
	statusBox.removeClass()
	statusBox.addClass("h2 alert text-center")
	switch(state.state){
	case BidderState.WAITING:
		if(roomOwner === username){
			statusBox.addClass("alert-success")
			statusBox.html("Ready to start")
		}else{
			statusBox.addClass("alert-warning")
			statusBox.html("Waiting for host to start")
		}
		break
	case BidderState.BIDDING:
		currentPlayer = state.activePlayer
		var statusStr = "It's " + (currentPlayer === username ? "your" : (state.activePlayer + "'s")) + " turn"
		statusBox.html(statusStr)

		if(currentPlayer === username){
			statusBox.addClass("alert-primary")
		}
		break
	case BidderState.ENDED:
		statusBox.addClass("alert-secondary")
		statusBox.html("Bidding has ended!")
		break
	}

	// Show/hide bid box
	if(state.activePlayer !== username){
		bidBox.hide()
		$(".bidding-entry .btn").attr("disabled", true)
	}else{
		$(".bidding-entry .btn").attr("disabled", false)
	}
}

function startBidding(){
	socket.emit('start', {roomId: roomId})
}

function submitBid(){
	socket.emit('bid', {
		roomId: roomId,
		combination: currentBidTarget,
		bidAmount: currentBidValue
	})
}

function leaveRoom(){
	socket.emit('leave', {roomId: roomId})
	document.location = '/'
}

function join(){
	socket.emit('join', {roomId: roomId, player: username})
}
