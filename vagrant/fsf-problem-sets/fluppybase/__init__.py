# start Flask app in subfolder following Simple Package structure
# http://flask.pocoo.org/docs/0.10/patterns/packages/#simple-packages
from flask import Flask
app = Flask (__name__)

# app routes/views for this project
# placed at bottom of file to avoid circular reference
import fluppybase.views