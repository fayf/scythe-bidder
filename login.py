from flask_login import LoginManager, UserMixin
login_manager = LoginManager()

class User(UserMixin):
	pass

# Users
users = {}

login_manager.login_view = 'routes.index'

@login_manager.user_loader
def user_loader(username):
	if username in users:
		return users[username]
	return None
