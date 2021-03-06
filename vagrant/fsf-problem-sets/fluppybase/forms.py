# sqlalchemy stuff
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker

# shelter balancing functions
from puppies_db_setup import get_occupancy, set_occupancy, set_capacity, check_in, curate_shelter_capacity, distribute_puppies

# setup connection for db
from puppies_db_setup import Base,Shelter,Puppy,Adopter,Profile
engine = create_engine ('sqlite:///fluppybase/puppies.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# for making forms classes
from wtforms import Form, BooleanField, TextField, RadioField, PasswordField, validators


# Form fields when user clicks to login
class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Required()])

# Form fields when users create or edit their profile
class AdopterForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    address = TextField('Address', [validators.Length(min=6, max=50)])
    city = TextField('City', [validators.Length(min=2, max=35)])
    state = TextField('State', [validators.Length(min=2, max=2)])
    zipCode = TextField('Zip', [validators.Length(min=2, max=6)])
    website = TextField('Website', [validators.Length(min=6, max=100)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
    	validators.Required(),
    	validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])

# Form fields when user adds or updates a puppy, including selecting its shelter
class PuppyForm(Form):
	shelters = session.query(Shelter).all()
	name = TextField('Name', [validators.Length(min=4, max=25)])
	breed = TextField('Breed', [validators.Length(min=6, max=25)])
	gender = TextField('Gender', [validators.Length(min=2, max=10)])
	weight = TextField('Weight', [validators.Length(min=2, max=25)])
	dateOfBirth = TextField('Birthdate', [validators.Length(min=2, max=10)])
	picture = TextField('Photo', [validators.Length(min=6, max=200)])
	shelter_id = RadioField('Shelter', [validators.Required()], choices=[('%s'%s.id,'%s'%s.name) for s in shelters])

# Form fields when user adds or updates a shelter
class ShelterForm(Form):
	shelters = session.query(Shelter).all()
	name = TextField('Name', [validators.Length(min=4, max=25)])
	address = TextField('Address', [validators.Length(min=6, max=50)])
	city = TextField('City', [validators.Length(min=2, max=35)])
	state = TextField('State', [validators.Length(min=2, max=10)])
	zipCode = TextField('Zip', [validators.Length(min=2, max=6)])
	website = TextField('Website', [validators.Length(min=6, max=150)])
	capacity = TextField('Capacity', [validators.Length(min=2, max=6)])
