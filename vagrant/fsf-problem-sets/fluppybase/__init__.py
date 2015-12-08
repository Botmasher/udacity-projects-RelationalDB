# start Flask app in subfolder following Simple Package structure
# http://flask.pocoo.org/docs/0.10/patterns/packages/#simple-packages
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def create_app():
	this_app = Flask (__name__)
	this_app.config.from_object('config')
	return this_app
	
app = create_app()

# setup db - app works without, but need this for flask_test testing with the db
db = SQLAlchemy(app)

# app mail set up in __init__; use to send messages - currently broken
from mail import Mail
mail = Mail(app)

# app routes/views for this project
# placed at bottom of file to avoid circular reference
import fluppybase.views