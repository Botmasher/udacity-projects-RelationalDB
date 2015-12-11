# cross-import from Flask app started in __init__.py
# following Simple Packages convention:
# http://flask.pocoo.org/docs/0.10/patterns/packages/#simple-packages
from fluppybase import app, mail

# basic flask stuff
from flask import render_template, request, redirect, url_for, flash, jsonify

# get my WTForms classes from forms.py file
from forms import LoginForm, AdopterForm, PuppyForm, ShelterForm

import math

# email functionality from mail package - currently broken
from mail.message import Message

# sqlalchemy stuff
from sqlalchemy import create_engine, func, distinct, asc, desc
from sqlalchemy.orm import sessionmaker

# shelter balancing functions
from puppies_db_setup import get_occupancy, set_occupancy, set_capacity, check_in, curate_shelter_capacity, distribute_puppies

# setup connection for db
from puppies_db_setup import Base,Shelter,Puppy,Adopter,Profile
engine = create_engine ('sqlite:///fluppybase/puppies.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# session-wide adopter id and name
logged_in = ['unknown','Login']

import whoosh
import whooshalchemy

# visit root
@app.route('/')
def homePage():
    # try to send an email
    #email_mssg = Message ('Hi there!', sender=('Test','me@example.com'), recipients=['myemail@mail.com'])
    #email_mssg.body = '<h1>Sending to you</h1><p>With FluppyBase kinda love.</p>'
    #mail.send (email_mssg)
    
    # try to test getting whoosh + whooshalchemy search results
    #search_results = Puppy.query.whoosh_search('Bailey').all()

    return redirect (url_for ('puppies'))

# simple login routine
@app.route('/login/<login_id>/', methods=['GET','POST'])
def login(login_id):
	# create form instance of forms.py class
	form = LoginForm (request.form)
	if request.method == 'POST' and form.validate():
		# if new user, prompt to create a profile
		try:
			user = session.query(Adopter).filter_by(name=form.username.data,password=form.password.data)[0]
		except:
			return redirect (url_for('add', table='adopter'))
		# sign in returning user
		logged_in[0] = user.id
		logged_in[1] = user.name
		flash ('Thanks for signing in!')
		return redirect (url_for('homePage'))

	# if not logged in, check for username and password
	if login_id == 'unknown':
		content = '<a href="%s">become an adopter</a>'%(url_for('add', table='adopter'))
		return render_template('form.php', form=form, login=logged_in, content=content)
	# if logged in, click name to update your profile
	else:
		return redirect (url_for('adopter',adopter_id=login_id))

	# if request.method == 'POST':
	# 	# if new user, prompt to create a profile
	# 	try:
	# 		user = session.query(Adopter).filter_by(name=request.form['name'],password=request.form['pwd'])[0]
	# 	except:
	# 		return redirect (url_for('add', table='adopter'))
	# 	logged_in[0] = user.id
	# 	logged_in[1] = user.name
	# 	return redirect (url_for('homePage'))

	# # if not logged in, check for username and password
	# if login_id == 'unknown':
	# 	output =  '<form action="" method="POST">'
	# 	output += '<p><input type="text" name="name" placeholder="Username"></p>'
	# 	output += '<p><input type="text" name="pwd" placeholder="password"></p>'
	# 	output += '<p><input type="submit" value="Login"> / <a href="%s">new user</a></p>'%(url_for('add',table='adopter'))
	# 	output += '</form>'
	# 	return render_template('main.php', login=logged_in, content=output)
	# # if logged in, click name to update your profile
	# else:
	# 	return redirect (url_for('adopter',adopter_id=login_id))


# browse all puppies
@app.route('/puppies/')
@app.route('/puppies/page/<int:page>')
def puppies(page=1):
	# get all puppies from db
	puppies = session.query(Puppy).all()
	pictures = session.query(Profile.picture).all()

	# link to add puppy form
	output = '<p><a href="%s">+ add a puppy</a></p>'%(url_for('add',table='puppy'))

	# link to paginate results if over a certain threshold
	p_count = session.query(func.count(distinct(Puppy.id))).first()[0] 	# how many puppies in db?
	results_per_page = 36.0 	# how many puppies to display on a single page?
	
	# cut results into chunks if there are more puppies than allowed on a page
	if p_count > results_per_page:
		# catch cutting list between page n and page n+1 results => index out of range
		try:
			# have multiple pages of results - just cut current page chunk from list
			puppies = [puppies[i] for i in range(int((page-1)*results_per_page),int(page*results_per_page))]
			pictures = [pictures[i] for i in range(int((page-1)*results_per_page),int(page*results_per_page))]
		except:
			# on last page with less than total results per page - get last chunk of list
			puppies = [puppies[i] for i in range(int((page-1)*results_per_page), len(puppies)-1)]
			pictures = [pictures[i] for i in range(int((page-1)*results_per_page), len(pictures)-1)]

		# list all available pages for viewer to access all results
		output += '<p style="text-align:center;">page '

		# divide this count up into pages and link to those pages
		for i in range( 0, int (math.ceil(p_count/results_per_page)) ):
			output += '&nbsp;<a href="%s">%s</a>'%(url_for('puppies',page=i+1), str(i+1))
		output += '</p>'

	# format each puppy entry within rows of puppy image/text
	counter = 0
	for p in puppies:
		# if image/text puppies reach the end of the row, create a new row to wrap around
		if counter > 5:
			# start a new row
			output += '</section><section class = row>'
			# reset puppies displayed in this row
			counter = 0
		# place the text/image block for this puppy
		output += '<div class="col-md-2">'
		output += '<h2><a href="/puppy/%s">%s</a></h2> <br><img src="%s" alt="puppy picture for %s" style="width: 10vw">'%(p.id,p.name,session.query(Profile).filter_by(id=p.id)[0].picture,p.name)
		output += '<br><a href="%s">edit</a> &nbsp; &nbsp;'%(url_for('edit',table='puppy',index=p.id))
		output += '<a href="%s">delete</a>'%(url_for('delete',table='puppy',index=p.id))
		output += '</div>'
		# count up how many puppies are displayed in this row so far
		counter += 1
	
	return render_template('main.php', login=logged_in, content=output)


# browse all shelters
@app.route('/shelters/', methods=['GET','POST'])
def shelters():
	if request.method == 'POST':
		# run load balancing algorithm to reassign puppies
		if logged_in[0]!='unknown':
			is_distributed = distribute_puppies()
		else:
			is_distributed = 'unknown'

		# display results from shelter load balancing
		if is_distributed == 'unknown':
			flash ("You must be logged in to run shelter rebalancing.")
		elif is_distributed:
			flash ("Rebalanced puppies among all shelters!")
		else:
			flash ("Unable to reassign puppies. Are shelters full?")
		
		return redirect (url_for('shelters'))

	# get all shelters from the db
	shelters = session.query(Shelter).all()
	output = '<p><a href="%s">+ add a shelter</a></p>'%(url_for('add',table='shelter'))
	output += '<p><form action="" method="POST"><input type="submit" value="Rebalance Puppies!"></form></p>'
	# iterate through and display shelters
	for s in shelters:
		output += '<h2><a href="/shelter/%s">%s</a></h2>'%(s.id,s.name)
		output += '<br>puppies: %s <br> capacity: %s'%(s.occupancy,s.capacity)
		output += '<br><a href="%s">edit</a> &nbsp; &nbsp;'%(url_for('edit',table='shelter',index=s.id))
		output += '<a href="%s">delete</a>'%(url_for('delete',table='shelter',index=s.id))
	
	return render_template('main.php', login=logged_in, content=output)


# select specific puppy profile and choose to adopt
@app.route('/puppy/<int:puppy_id>/', methods=['GET','POST'])
def puppy(puppy_id):
	# adopt the puppy or warn that user is not logged in to adopt
	if request.method == 'POST':
		if logged_in[0] == 'unknown':
			flash("Please login or create a profile to adopt puppies.")
		else:
			adopter = session.query(Adopter).filter_by(id=logged_in[0]).first()
			adopter.puppy_id = puppy_id
			puppy = session.query(Puppy).filter_by(id=puppy_id).first()
			session.commit()
			flash("Thank you for adopting a puppy! Click your profile to see all your puppies.")
			app.logger.info ('%s adopted puppy %s'%(adopter.name, puppy.name))
		return redirect (url_for('homePage'))

	# get the puppy and associated profile
	puppy = session.query(Puppy).filter_by(id=puppy_id).first()
	profile = session.query(Profile).filter_by(id=puppy_id).first()
	shelter = session.query(Shelter).filter_by(id=puppy.shelter_id).first()
	# read puppy info to user
	output = '<h2>%s</h2>\
				<img src="%s">\
				<p>Breed: %s</p>\
				<p>Home shelter: <a href="%s">%s</a></p>\
				<p>Gender: %s</p>\
				<p>Date of birth: %s</p>\
				<p>Weight: %s</p>\
				<p>Left ear: sloppy</p>\
				<p>Right ear: blopsy</p>'%(puppy.name, profile.picture, profile.breed, url_for('shelter',shelter_id=shelter.id), shelter.name, profile.gender, profile.dateOfBirth, profile.weight)
	
	# button for adopting this puppy if not already adopted
	if session.query(Adopter).filter_by(puppy_id=puppy_id).first() == None:
		output += '<p><br><form action="" method="POST">\
				   <a href ="%s">edit my profile</a> &nbsp;&nbsp;\
				   <input type="submit" value="Adopt me!"></form></p>'%url_for('edit',table='puppy',index=puppy_id)
	else:
		output += '<p><em>Someone adopted me! I have a home now!</em></p>'
	
	return render_template('main.php', login=logged_in, content=output)


# select specific shelter profile
@app.route('/shelter/<int:shelter_id>/')
def shelter(shelter_id):
	# get the puppy and associated profile
	shelter = session.query(Shelter).filter_by(id=shelter_id).first()
	output = '<h2>%s</h2>\
			   <p>%s<br>%s, %s %s<br><a href="%s">%s</a></p>'%(shelter.name, shelter.address, shelter.city, shelter.state, shelter.zipCode, shelter.website, shelter.website)
	return render_template('main.php', login=logged_in, content=output)


# view specific adopter profile
@app.route('/adopter/<int:adopter_id>/')
def adopter(adopter_id):
	adopter = session.query(Adopter).filter_by(id=adopter_id).first()
	my_puppy = session.query(Puppy).filter_by(id=adopter.puppy_id).first()
	my_puppy_profile = session.query(Profile).filter_by(id=adopter.puppy_id).first()
	
	# display user's information kept on file
	output = '<p>Please keep your puppy lovin info up to date!</p>'
	output += '<h2>%s</h2><p>%s<br>%s, %s %s<br>%s<br>%s</p>' % (adopter.name, adopter.address, adopter.city, adopter.state, adopter.zipCode, adopter.email, adopter.website)

	# prompt user to edit info - redirects to the /edit/Adopter/id form
	output += '<p><a href = "%s">Edit my info</a></p>' % (url_for('edit',table='adopter',index=adopter_id))

	# display adopted puppies if you have any
	if my_puppy != None:
		output += '<h2>Puppies I\'ve adopted</h2>'
		output += '<p><img src="%s" alt="picture of puppy %s"><br><a href="%s">%s</a></p>' % (my_puppy_profile.picture, my_puppy.name, url_for('puppy',puppy_id=my_puppy.id), my_puppy.name)

	return render_template('main.php', login=logged_in, content=output)


# add to a table - Puppy, Shelter or Adopter
@app.route('/add/<table>/', methods=['GET','POST'])
def add (table):

	# retrieve form class for this URL keyword
	if table == 'adopter':
		form = AdopterForm(request.form)
	elif table == 'puppy':
		shelters = session.query(Shelter).all()
		form = PuppyForm (request.form)
	elif table == 'shelter':
		form = ShelterForm (request.form)
	else:
		flash ('This isn\'t the /add/ you are looking for! We don\'t recognize that URL. Please try adding a /puppy, /shelter or /adopter.')
		return redirect (url_for('homePage'))

	# add to database on form submission
	if request.method == 'POST' and form.validate():

		if table == 'adopter':
			new_row = Adopter (name=form.username.data, address=form.address.data, city=form.city.data, state=form.state.data, zipCode=form.zipCode.data, website=form.website.data, email=form.email.data, password=form.password.data)
			flash ('Thank you for creating an Adopter profile!')

		elif table == 'puppy':
			# try checking puppy in to shelter if shelter not full
			new_row = Puppy (name=form.name.data, shelter_id=form.shelter_id.data)
			if session.query(Shelter).filter_by(id=new_row.shelter_id)[0].occupancy >= session.query(Shelter).filter_by(id=new_row.shelter_id)[0].capacity:
				# HOMELESS! - we can't place the puppy!
				new_row.shelter_id = None
				flash("Unable to place puppy - currently has no home shelter!")
			# create profile entry for this puppy too
			new_profile = Profile (puppy_id=new_row.id, breed=form.breed.data, gender=form.gender.data, weight=form.weight.data, picture=form.picture.data)
			session.add (new_profile)
			flash ('Thank you for adding a puppy!')
			app.logger.info ('Added puppy %s to FluppyBase'%(new_row.name))

		elif table == 'shelter':
			new_row = Shelter (name=form.name.data, address=form.address.data, zipCode=form.zipCode.data, city=form.city.data, state=form.state.data, website=form.website.data, capacity=form.capacity.data)
			flash ('Thank you for adding a shelter!')

		else:
			flash ('Unable to add your info to FluppyBase (*whimper*). Don\'t leave yet! Please check that the form is completely filled out.')
			return redirect (url_for ('add', table=table))

		# add created row to db
		session.add (new_row)
		session.commit()
		# update shelter totals
		curate_shelter_capacity()
		return redirect (url_for('homePage'))

	# elif request.method=='POST':

	# 	# check if any input fields are empty - send user back to this page
	# 	for i in request.form:
	# 		if request.form[i] == '' or request.form[i] == None:
	# 			return redirect (url_for ('add', table=table))

	# 	# add row to shelter table
	# 	if table == 'shelter':
	# 		new_row = Shelter (name=request.form['name'], address=request.form['address'], city=request.form['city'], zipCode=request.form['zipcode'], state=request.form['state'], website=request.form['website'], capacity=request.form['capacity'])
		
	# 	# add row to adopter table
	# 	elif table == 'adopter':
	# 		new_row = Adopter (name=request.form['name'], address=request.form['address'], city=request.form['city'], zipCode=request.form['zipcode'], state=request.form['state'], website=request.form['website'], email=request.form['email'], password=request.form['pwd'])
		
	# 	# add row to puppy table
	# 	elif table == 'puppy':
	# 		# try checking puppy in to shelter if shelter not full
	# 		new_row = Puppy (name=request.form['name'], shelter_id=request.form['shelterID'])
	# 		if session.query(Shelter).filter_by(id=new_row.shelter_id)[0].occupancy >= session.query(Shelter).filter_by(id=new_row.shelter_id)[0].capacity:
	# 			# HOMELESS! - we can't place the puppy!
	# 			new_row.shelter_id = None
	# 			flash("Unable to place puppy - currently has no home shelter!")
	# 		# create profile entry for this puppy too
	# 		new_profile = Profile (puppy_id=new_row.id, breed=request.form['breed'], gender=request.form['gender'], weight=request.form['weight'], picture=request.form['picture'])
	# 		session.add (new_profile)
		
	# 	# found no table for this url variable
	# 	else:
	# 		return redirect (url_for ('homePage'))

	# 	# add whichever row was created above to the db
	# 	session.add (new_row)
	# 	session.commit()
	# 	# update shelter totals
	# 	curate_shelter_capacity()
	# 	# go home
	# 	return redirect (url_for('homePage'))

	# if method is GET display form for user input
	#output = '<form action="" method="POST">'
	
	# check which table user is adding to, then build form for that table
	if table == 'shelter':
		return render_template('form.php', form=form, login=logged_in, content='')
		# output += '<h2>Add one shelter!</h2>'
		# output += '<p>Name: <input type="text" name="name"></p>\
		# <p>Address: <input type="text" name="address"></p>\
		# <p>City: <input type="text" name="city"></p>\
		# <p>Zip: <input type="text" name="zipcode"></p>\
		# <p>State: <input type="text" name="state"></p>\
		# <p>Website: <input type="text" name="website"></p>\
		# <p>Capacity: <input type="text" name="capacity"></p>'

	elif table == 'adopter':
		return render_template('form.php', form=form, login=logged_in, content='')
		# output += '<h2>Become an adopter!</h2>'
		# output += '<p>User: <input type="text" name="name"></p>'
		# output += '<p>Address: <input type="text" name="address"></p>'
		# output += '<p>City: <input type="text" name="city"></p>'
		# output += '<p>State: <input type="text" name="state"></p>'
		# output += '<p>Zip: <input type="text" name="zipcode"></p>'
		# output += '<p>Website: <input type="text" name="website"></p>'
		# output += '<p>Email: <input type="text" name="email"></p>'
		# output += '<p>Password: <input type="text" name="pwd"></p>'

	elif table == 'puppy':
		# set shelter_id radio buttons to a specific button (here the second shelter)
		form.shelter_id.data='%s'%session.query(Shelter).order_by(asc(Shelter.id))[1].id
		# render the form
		return render_template('form.php', form=form, login=logged_in, content='')
		# output += '<h2>Add one puppy!</h2>'
		# output += '<p>Name: <input type="text" name="name"></p>\
		# <p>Breed: <input type="text" name="breed"></p>\
		# <p>Gender: <input type="radio" name="gender" value="male"> M <input type="radio" name="gender" value="female"> F</p>\
		# <p>Weight: <input type="text" name="weight"></p>\
		# <p>Date of birth: <input type="text" name="dateOfBirth"></p>\
		# <p>Picture: <input type="text" name="picture"></p>\
		# <p>Choose a Home Shelter for this puppy: <br>'
		# # radio button select from existing shelters
		# shelters = session.query(Shelter).all()
		# for s in shelters:
		# 	output += '<input type="radio" name="shelterID" value="%s"> %s<br>'%(s.id, s.name)
		# output += '</p>'

	# found no such table for this url var
	else:
		return redirect (url_for ('homePage'))
	
	# end form and page - submit to reach POST branch above
	#output += '<p><input type="submit" value="Add"></p></form>'

	#return render_template('main.php', login=logged_in, content=output)


# update a puppy, shelter or adopter in a table
@app.route('/edit/<table>/<int:index>/', methods=['GET','POST'])
def edit (table, index):

	# retrieve form class from forms.py based on URL keyword
	if table == 'adopter':
		form = AdopterForm(request.form)
	elif table == 'puppy':
		shelters = session.query(Shelter).all()
		form = PuppyForm (request.form)
	elif table == 'shelter':
		form = ShelterForm (request.form)
	else:
		flash ('This isn\'t the /edit/ you are looking for! We don\'t recognize that URL. Please try editing a /puppy, /shelter or /adopter.')
		return redirect (url_for('homePage'))

	# edit database on form submission
	if request.method == 'POST' and form.validate():

		# your edit URL ends in /adopter/
		if table == 'adopter':
			mod_row = session.query(Adopter).filter_by(id=index)[0]
			mod_row.name = form.username.data
			mod_row.address = form.address.data
			mod_row.city = form.city.data
			mod_row.state = form.state.data
			mod_row.zipCode = form.zipCode.data
			mod_row.website = form.website.data
			mod_row.email = form.email.data
			mod_row.password = form.password.data
			flash ('Your Adopter profile has been updated!')

		# your edit URL ends in /puppy/
		elif table == 'puppy':
			# update the puppy name and shelter
			mod_row = session.query(Puppy).filter_by(id=index)[0]
			previous_shelter = mod_row.shelter_id
			mod_row.name = form.name.data
			mod_row.shelter_id = form.shelter_id.data
			# if chosen shelter is full, place puppy back in its current shelter
			if session.query(Shelter).filter_by(id=mod_row.shelter_id)[0].occupancy >= session.query(Shelter).filter_by(id=mod_row.shelter_id)[0].capacity:
				mod_row.shelter_id = previous_shelter
				flash("You selected a FULL shelter! Your puppy will stay in the current home shelter.")
			# update the profile entry for this puppy as well
			mod_profile = session.query(Profile).filter_by(id=index)[0]
			mod_profile.puppy_id = index
			mod_profile.breed = form.breed.data
			mod_profile.gender = form.gender.data
			mod_profile.weight = form.weight.data
			mod_profile.picture = form.picture.data
			session.add (mod_profile)
			flash ('Your puppy\'s info has been updated!')

		# your edit URL ends in /shelter/
		elif table == 'shelter':
			mod_row = session.query(Shelter).filter_by(id=index)[0]
			mod_row.name = form.name.data
			mod_row.address = form.address.data
			mod_row.zipCode = form.zipCode.data
			mod_row.city = form.city.data
			mod_row.state = form.state.data
			mod_row.website = form.website.data
			mod_row.capacity = form.capacity.data
			flash ('Your shelter\'s info has been updated!')

		else:
			flash ('Unable to add your info to FluppyBase (*whimper*). Don\'t leave yet! Please check that the form is completely filled out.')
			return redirect (url_for ('edit', table=table, index=index))

		# update row in the db
		session.add (mod_row)
		session.commit()
		# update shelter totals
		curate_shelter_capacity()
		return redirect (url_for('homePage'))

	# check which table user is updating, then build form for that table
	if table == 'shelter':
		this_shelter = session.query(Shelter).filter_by(id=index)[0]
		form.name.data = this_shelter.name
		form.address.data = this_shelter.address
		form.city.data = this_shelter.city
		form.state.data = this_shelter.state
		form.zipCode.data = this_shelter.zipCode
		form.website.data = this_shelter.website
		form.capacity.data = this_shelter.capacity
		return render_template('form.php', form=form, login=logged_in, content='')

	elif table == 'adopter':
		this_adopter = session.query(Adopter).filter_by(id=index)[0]
		form.username.data = this_adopter.name
		form.address.data = this_adopter.address
		form.city.data = this_adopter.city
		form.state.data = this_adopter.state
		form.zipCode.data = this_adopter.zipCode
		form.website.data = this_adopter.website
		form.email.data = this_adopter.email
		return render_template('form.php', form=form, login=logged_in, content='')

	elif table == 'puppy':
		# set the default fields
		this_puppy = session.query(Puppy).filter_by(id=index)[0]
		this_profile = session.query(Profile).filter_by(id=index)[0]
		form.name.data = this_puppy.name
		form.breed.data = this_profile.breed
		form.gender.data = this_profile.gender
		form.weight.data = this_profile.weight
		form.dateOfBirth.data = this_profile.dateOfBirth
		form.picture.data = this_profile.picture
		# set shelter_id radio buttons to a specific button (here the second shelter)
		form.shelter_id.data='%s'%this_puppy.shelter_id
		# render the form
		return render_template('form.php', form=form, login=logged_in, content='')

	# found no such table for this url var
	else:
		return redirect (url_for ('homePage'))

	# # edit database on form submission
	# if request.method=='POST':

	# 	# check if any input fields are empty - send user back to this page
	# 	for i in request.form:
	# 		if request.form[i] == '' or request.form[i] == None:
	# 			return redirect (url_for ('edit', table=table, index=index))

	# 	# add row to shelter table
	# 	if table == 'shelter':
	# 		mod_row = session.query(Shelter).filter_by(id=index)[0]
	# 		mod_row.name = request.form['name']
	# 		mod_row.address = request.form['address']
	# 		mod_row.city = request.form['city']
	# 		mod_row.zipCode = request.form['zipcode']
	# 		mod_row.state = request.form['state']
	# 		mod_row.website = request.form['website']
	# 		mod_row.capacity = request.form['capacity']
		
	# 	# add row to adopter table
	# 	elif table == 'adopter':
	# 		mod_row = session.query(Adopter).filter_by(id=index)[0]
	# 		mod_row.name = request.form['name']
	# 		mod_row.address = request.form['address']
	# 		mod_row.city = request.form['city']
	# 		mod_row.zipCode = request.form['zipcode']
	# 		mod_row.state = request.form['state']
	# 		mod_row.email = request.form['email']
	# 		mod_row.website = request.form['website']
	# 		mod_row.password = request.form['password']
		
	# 	# add row to puppy table
	# 	elif table == 'puppy':
	# 		mod_row = session.query(Puppy).filter_by(id=index)[0]
	# 		mod_row.name = request.form['name']
	# 		last_id = mod_row.shelter_id	# store current shelter in case new one is full
	# 		mod_row.shelter_id = request.form['shelterID']
	# 		mod_profile = session.query(Profile).filter_by(id=index)[0]
	# 		mod_profile.breed = request.form['breed']
	# 		mod_profile.gender = request.form['gender']
	# 		mod_profile.weight = request.form['weight']
	# 		mod_profile.picture = request.form['picture']
	# 		session.add (mod_profile)
	# 		# catch overflow puppies and unassign from full shelter
	# 		if session.query(Shelter).filter_by(id=mod_row.shelter_id)[0].occupancy >= session.query(Shelter).filter_by(id=mod_row.shelter_id)[0].capacity:
	# 			# shelter full - move to previous shelter
	# 			flash("Shelter full! Unable to move puppy - staying in current home shelter!")
	# 			mod_row.shelter_id = last_id				

	# 	# found no table corresponding to url var - return home instead
	# 	else:
	# 		return redirect(url_for('homePage'))

	# 	# edit row updated above in the db
	# 	session.add (mod_row)
	# 	session.commit()
	# 	# update shelter totals
	# 	curate_shelter_capacity()
	# 	return redirect (url_for('homePage'))

	# if method is GET display form for user input
	output = '<form action="" method="POST">'
	
	# check which table user is adding to, then display inputs for that table
	if table == 'shelter':
		# read and display data for this shelter
		s = session.query(Shelter).filter_by(id=index)[0]
		output += '<h2>Edit this shelter!</h2>'
		output += '<p>Name: <input type="text" name="name" value="%s"></p>\
		<p>Address: <input type="text" name="address" value="%s"></p>\
		<p>City: <input type="text" name="city" value="%s"></p>\
		<p>Zip: <input type="text" name="zipcode" value="%s"></p>\
		<p>State: <input type="text" name="state" value="%s"></p>\
		<p>Website: <input type="text" name="website" value="%s"></p>\
		<p>Capacity: <input type="text" name="capacity" value="%s"></p>'%(s.name,s.address,s.city,s.zipCode,s.state,s.website,s.capacity)

	# read and display data for this adopter
	elif table == 'adopter':
		a = session.query(Adopter).filter_by(id=index)[0]
		output += '<h2>Edit this adopter!</h2>'
		output += '<p>Name: <input type="text" name="name" value="%s"><br>\
				   <p>Address: <input type="text" name="address" value="%s"><br>\
				   <p>City: <input type="text" name="city" value="%s"><br>\
				   <p>State: <input type="text" name="state" value="%s"><br>\
				   <p>Zip: <input type="text" name="zipcode" value="%s"><br>\
				   <p>Email: <input type="text" name="email" value="%s"><br>\
				   <p>Website: <input type="text" name="website" value="%s"><br>\
				   <p>Password: <input type="text" name="password"><br>'%(a.name, a.address, a.city, a.state, a.zipCode, a.email, a.website)
	
	# read and display puppy and profile info
	elif table == 'puppy':
		p = session.query(Puppy).filter_by(id=index)[0]
		q = session.query(Profile).filter_by(id=index)[0]
		output += '<h2>Edit this puppy!</h2>'
		output += '<p>Name: <input type="text" name="name" value="%s"></p>\
		<p>Breed: <input type="text" name="breed" value="%s"></p>'%(p.name,q.breed)
		# set the radio button for current profile gender as selected
		if (q.gender == 'male'):
			output += '<p>Gender: <input type="radio" name="gender" value="male" checked> M <input type="radio" name="gender" value="female"> F</p>'
		else:
			output += '<p>Gender: <input type="radio" name="gender" value="male"> M <input type="radio" name="gender" value="female" checked> F</p>'
		# read and display profile
		output += '<p>Weight: <input type="text" name="weight" value="%s"></p>\
		<p>Date of birth: <input type="text" name="dateOfBirth" value="%s"></p>\
		<p>Picture: <input type="text" name="picture" value="%s"></p>\
		<p>Choose a Home Shelter for this puppy: <br>'%(q.weight,q.dateOfBirth,q.picture)
		# select from existing shelters
		shelters = session.query(Shelter).all()
		for s in shelters:
			if (s.id == p.shelter_id):
				output += '<input type="radio" name="shelterID" value="%s" checked>'%s.id
			else:
				output += '<input type="radio" name="shelterID" value="%s">'%s.id
			output += ' &nbsp;%s<br>'%s.name
		output += '</p>'

	# found no table for this url variable - return home instead
	else:
		return redirect (url_for('homePage'))

	# end form and page - submit to reach POST branch above
	output += '<p><input type="submit" value="Modify"></p></form>'

	return render_template('main.php', login=logged_in, content=output)


# delete a Shelter, Puppy (including Profile) or Adopter from a table
@app.route('/delete/<table>/<int:index>/', methods=['GET','POST'])
def delete (table, index):

	# check which table user is deleting from
	if table == 'shelter':
		this_entry = session.query(Shelter).filter_by(id=index)[0]
	elif table == 'adopter':
		this_entry = session.query(Adopter).filter_by(id=index)[0]
	elif table == 'puppy':
		this_entry = session.query(Puppy).filter_by(id=index)[0]
	# url variable does not relate to a table - return home instead
	else:
		return redirect (url_for('homePage'))

	if request.method=='POST':		
		# if deleting puppy, delete row from profile table as well
		if table == 'puppy':
			this_profile = session.query(Profile).filter_by(id=index)[0]
			session.delete (this_profile)

		# if deleting shelter or adopter, continue
		elif table == 'shelter' or table == 'adopter':
			pass

		# if url variable matches no table, redirect
		else:
			return redirect (url_for ('homePage'))

		# edit row updated above in the db
		session.delete (this_entry)
		session.commit()
		# update shelter totals
		curate_shelter_capacity()
		return redirect (url_for('homePage'))
	
	# if method is GET display form for user to confirm the delete
	
	# end form and page - submit to reach POST branch above
	output = '<form action="" method="POST">'
	output += '<h2>Are you sure you want to delete %s?</h2>'%(this_entry.name)
	output += '<p>This action cannot be undone!</p>\
			   <p><input type="submit" value="Delete"></p></form>'

	return render_template('main.php', login=logged_in, content=output)


# catch requests for JSON data
@app.route('/puppy/<int:puppy_id>/JSON/')
def puppyJSON(puppy_id):
	# query for appropriate items
	puppy = session.query(Puppy).filter_by(id=puppy_id).one()
	# json using @property serialize defined in orm class file
	return jsonify(Puppy = [puppy.serialize])

@app.route('/puppies/JSON/')
def puppiesJSON():
	puppies = session.query(Puppy).all()
	return jsonify(Puppies = [p.serialize for p in puppies])

@app.route('/profile/<int:profile_id>/JSON/')
def profileJSON(profile_id):
	profile = session.query(Profile).filter_by(id=profile_id).one()
	return jsonify(Profile = [profile.serialize])

@app.route('/profiles/JSON/')
def profilesJSON():
	profiles = session.query(Profile).all()
	return jsonify(Profiles = [p.serialize for p in profiles])

@app.route('/shelter/<int:shelter_id>/JSON/')
def shelterJSON(shelter_id):
	shelter = session.query(Shelter).filter_by(id=shelter_id).one()
	return jsonify(Shelter = [shelter.serialize])

@app.route('/shelters/JSON/')
def sheltersJSON():
	shelters = session.query(Shelter).all()
	return jsonify(Shelters = [s.serialize for s in shelters])

@app.route('/adopter/<int:adopter_id>/JSON/')
def adopterJSON(adopter_id):
	adopter = session.query(Adopter).filter_by(id=adopter_id).one()
	return jsonify(Adopter = [adopter.serialize])

@app.route('/adopters/JSON/')
def adoptersJSON():
	adopters = session.query(Adopter).all()
	return jsonify(Adopters = [a.serialize for a in adopters])


# run if this is app but not if imported as module
#if __name__ == '__main__':
#if __name__ == 'fluppybase.views':
# 	# reload server every time notice code change
# 	app.debug = True
# 	# session secret key for message flashing
# 	app.secret_key = 'super_secret_key'
# 	# for accessing and running on vagrant
# 	app.run(host = '0.0.0.0', port = 8000)