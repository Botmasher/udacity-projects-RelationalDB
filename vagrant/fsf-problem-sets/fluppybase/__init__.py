# start Flask app in subfolder following Simple Package structure
# http://flask.pocoo.org/docs/0.10/patterns/packages/#simple-packages
from flask import Flask

app = Flask (__name__)
app.config.from_object('config')

# app mail set up in __init__; use to send messages - currently broken
from mail import Mail
mail = Mail(app)

# app routes/views for this project
# placed at bottom of file to avoid circular reference
import fluppybase.views