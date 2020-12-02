import functools
from flask import session, flash
from flask_socketio import emit, join_room, leave_room, disconnect, close_room
from flask_login import current_user
from routes import rooms

def authenticated_only(f):
	@functools.wraps(f)
	def wrapped(*args, **kwargs):
		if not current_user.is_authenticated:
			disconnect()
		else:
			return f(*args, **kwargs)
	return wrapped

def register_events(socketio):
	@socketio.on('enter', namespace='/room')
	@authenticated_only
	def enter(message):
		room_id = message['roomId']
		join_room(room_id)

		bidding_room = rooms[room_id]
		emit('state', {'state': bidding_room.bidder.generate_state()}, room=room_id)

	@socketio.on('join', namespace='/room')
	@authenticated_only
	def join(message):
		room_id = message['roomId']
		rooms[room_id].add_player(current_user.id)
		bidding_room = rooms[room_id]

		emit('state', {'state': bidding_room.bidder.generate_state()}, room=room_id)

	@socketio.on('start', namespace='/room')
	@authenticated_only
	def start(message):
		room_id = message['roomId']
		bidding_room = rooms[room_id]
		bidding_room.start_bidding()
		emit('state', {'state': bidding_room.bidder.generate_state()}, room=room_id)

	@socketio.on('bid', namespace='/room')
	@authenticated_only
	def bid(message):
		room_id = message['roomId']
		bidding_room = rooms[room_id]

		bidding_room.bidder.process_bid(current_user.id, tuple(message['combination']), message['bidAmount'])
		emit('state', {'state': bidding_room.bidder.generate_state()}, room=room_id)

	@socketio.on('leave', namespace='/room')
	@authenticated_only
	def leave(message):
		room_id = message['roomId']
		leave_room(room_id)
		bidding_room = rooms[room_id]
		bidding_room.bidder.remove_player(current_user.id)

		if bidding_room.owner == current_user.id:
			emit('close', {}, room=room_id)
			close_room(room_id)
			rooms.pop(room_id)
			print(rooms)
		else:
			emit('state', {'state': bidding_room.bidder.generate_state()}, room=room_id)
