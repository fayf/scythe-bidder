from flask import Blueprint, render_template, flash, redirect, url_for, Flask, request, session
from flask_login import login_user, logout_user, login_required, current_user

from room import BiddingRoom
from login import User, login_manager, users

routes = Blueprint('routes', __name__)

rooms = {
}

@routes.after_request
def add_header(response):
	response.cache_control.max_age = 1
	return response

@routes.route('/')
def index():
	if current_user.is_anonymous:
		return render_template('login.html')
	return render_template('index.html', rooms=rooms)

@routes.route('/login', methods=["POST"])
def login():
	if 'username' not in request.form:
		return redirect(url_for('.index'))

	username = request.form['username']

	if username in users:
		flash('User {0} already exists!'.format(username), 'danger')
		return redirect(url_for('.index'))

	user = User()
	user.id = request.form['username']
	users[user.id] = user
	login_user(user)

	flash('Logged in as {0}.'.format(user.id), 'success')

	return redirect(url_for('.index'))

@routes.route('/logout')
def logout():
	if not current_user.is_anonymous:
		users.pop(current_user.id)

	logout_user()
	flash('Logged out.', 'success')
	return redirect(url_for('.index'))

@routes.route('/room', methods=["POST"])
@login_required
def room_new():
	player_name = current_user.id
	if 'roomName' in request.form and request.form['roomName']:
		room_name = request.form['roomName']
	else:
		room_name = '{0}\'s room'.format(player_name)

	rooms[room_name] = BiddingRoom(room_name, player_name)
	print("{0} created!".format(room_name))

	return redirect(url_for('.room', room_id=room_name))

@routes.route('/room/<room_id>')
@login_required
def room(room_id):
	if room_id not in rooms:
		flash('Room {0} not found'.format(room_id), 'warning')
		return redirect(url_for('.index'))

	return render_template('room.html', room=rooms[room_id])
