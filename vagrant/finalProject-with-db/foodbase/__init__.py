# start Flask app in subfolder following Simple Package structure
# http://flask.pocoo.org/docs/0.10/patterns/packages/#simple-packages
from flask import Flask
#from flask_sqlalchemy import SQLAlchemy

def create_app():
	this_app = Flask (__name__)
	this_app.config.from_object('config')
	return this_app
	
app = create_app()

# app routes/views for this project
# placed at bottom of file to avoid circular reference
import foodbase.views