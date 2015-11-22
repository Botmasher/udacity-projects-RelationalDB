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

from wtforms import Form, BooleanField, TextField, RadioField, PasswordField, validators

class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Required()])


class AdopterForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    address = TextField('Address', [validators.Length(min=6, max=50)])
    city = TextField('City', [validators.Length(min=2, max=35)])
    zipCode = TextField('Zip', [validators.Length(min=2, max=35)])
    state = TextField('State', [validators.Length(min=2, max=2)])
    website = TextField('Website', [validators.Length(min=6, max=50)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
    	validators.Required(),
    	validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])

class PuppyForm(Form):
	shelters = session.query(Shelter).all()
	name = TextField('Name', [validators.Length(min=4, max=25)])
	breed = TextField('Breed', [validators.Length(min=6, max=50)])
	gender = TextField('Gender', [validators.Length(min=2, max=35)])
	weight = TextField('Weight', [validators.Length(min=2, max=35)])
	dateOfBirth = TextField('Birthdate', [validators.Length(min=2, max=2)])
	picture = TextField('Photo', [validators.Length(min=6, max=50)])
	shelter = TextField('TestShelterTextBox', [validators.Length(min=6, max=35)])
	shelter_id = RadioField('Shelter', [validators.Required()], choices=[('%s'%s.id,'%s'%s.name) for s in shelters],
    	default='1')

	# # check which table user is adding to, then build form for that table
	# if table == 'shelter':
	# 	output += '<h2>Add one shelter!</h2>'
	# 	output += '<p>Name: <input type="text" name="name"></p>\
	# 	<p>Address: <input type="text" name="address"></p>\
	# 	<p>City: <input type="text" name="city"></p>\
	# 	<p>Zip: <input type="text" name="zipcode"></p>\
	# 	<p>State: <input type="text" name="state"></p>\
	# 	<p>Website: <input type="text" name="website"></p>\
	# 	<p>Capacity: <input type="text" name="capacity"></p>'

	# elif table == 'adopter':
	# 	output += '<h2>Become an adopter!</h2>'
	# 	output += '<p>User: <input type="text" name="name"></p>'
	# 	output += '<p>Address: <input type="text" name="address"></p>'
	# 	output += '<p>City: <input type="text" name="city"></p>'
	# 	output += '<p>State: <input type="text" name="state"></p>'
	# 	output += '<p>Zip: <input type="text" name="zipcode"></p>'
	# 	output += '<p>Website: <input type="text" name="website"></p>'
	# 	output += '<p>Email: <input type="text" name="email"></p>'
	# 	output += '<p>Password: <input type="text" name="pwd"></p>'

	# elif table == 'puppy':
	# 	output += '<h2>Add one puppy!</h2>'
	# 	output += '<p>Name: <input type="text" name="name"></p>\
	# 	<p>Breed: <input type="text" name="breed"></p>\
	# 	<p>Gender: <input type="radio" name="gender" value="male"> M <input type="radio" name="gender" value="female"> F</p>\
	# 	<p>Weight: <input type="text" name="weight"></p>\
	# 	<p>Date of birth: <input type="text" name="dateOfBirth"></p>\
	# 	<p>Picture: <input type="text" name="picture"></p>\
	# 	<p>Choose a Home Shelter for this puppy: <br>'
	# 	# radio button select from existing shelters
	# 	shelters = session.query(Shelter).all()
	# 	for s in shelters:
	# 		output += '<input type="radio" name="shelterID" value="%s"> %s<br>'%(s.id, s.name)
	# 	output += '</p>'

	# # found no such table for this url var
	# else:
	# 	return redirect (url_for ('homePage'))
	
	# # end form and page - submit to reach POST branch above
	# output += '<p><input type="submit" value="Add"></p></form>'

	# return render_template('main.php', login=logged_in, content=output)
