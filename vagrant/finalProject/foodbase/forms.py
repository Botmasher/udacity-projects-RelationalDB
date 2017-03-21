# sqlalchemy imports
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker

# setup connection for db
from models import Base, Restaurant, MenuItem, User
engine = create_engine ('sqlite:///foodbase/modelswithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# for making forms classes
from wtforms import Form, BooleanField, TextField, RadioField, PasswordField, validators

# Form fields when user clicks to login
class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Required()])

# Form fields when user adds or updates a restaurant
class RestaurantForm(Form):
	name = TextField('Name', [validators.Length(min=2, max=80)])
	cuisine = TextField('Cuisine', [validators.Length(min=4, max=100)])
	address = TextField('Address', [validators.Length(min=6, max=250)])
	city = TextField('City', [validators.Length(min=2, max=100)])
	zipCode = TextField('Zip Code', [validators.Length(min=5, max=5)])
	state = TextField('State', [validators.Length(min=2, max=80)])
	website = TextField('Website', [validators.Length(min=5, max=250)])
	image = TextField('Image', [validators.Length(min=5, max=250)])

# Form fields when user adds or updates menu item, including its restaurant
class MenuItemForm (Form):
	restaurants = session.query(Restaurant).all()
	name = TextField('Item name', [validators.Length(min=2, max=250)])
	description = TextField('Description', [validators.Length(min=5, max=800)])
	restaurant_id = RadioField('Restaurant', [validators.Required()], choices=[('%s'%r.id,'%s'%r.name) for r in restaurants])