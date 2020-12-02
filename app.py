import datetime
from flask_login import current_user
from flask import Blueprint, render_template, flash, redirect, url_for, Flask, session, g
from flask_socketio import SocketIO

from login import login_manager
from routes import routes
from events import register_events

socketio = SocketIO(async_mode='eventlet', cors_allowed_origins='*')

def create_app():
	app = Flask('scythe-bidder')
	app.secret_key = b'dQ8$76oMozy8'
	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
	# app.debug = True

	app.register_blueprint(routes)

	register_events(socketio)

	# @app.before_request
	# def before_request():
	# 	session.permanent = True
	# 	app.permanent_session_lifetime = datetime.timedelta(minutes=1)
	# 	session.modified = True
	# 	g.user = current_user

	socketio.init_app(app)
	login_manager.init_app(app)
	return app

if __name__ == '__main__':
	app = create_app()
	socketio.run(app, host="0.0.0.0")
