# basic flask stuff
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask (__name__)

# sqlalchemy stuff
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# shelter balancing functions
from puppies_db_setup import get_occupancy, set_occupancy, set_capacity, check_in, curate_shelter_capacity, distribute_puppies

# setup connection for restaurant db
from puppies_db_setup import Base,Shelter,Puppy,Adopter,Profile
engine = create_engine ('sqlite:///puppies.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# session-wide adopter id and name
logged_in = ['unknown','Login']

# visit root
@app.route('/')
def homePage():
	return redirect (url_for ('puppies'))
#	return render_template('main.php', login=logged_in)

# simple login routine
@app.route('/login/<login_id>/', methods=['GET','POST'])
def login(login_id):
	if request.method == 'POST':
		# if new user, prompt to create a profile
		try:
			user = session.query(Adopter).filter_by(name=request.form['name'],password=request.form['pwd'])[0]
		except:
			return redirect (url_for('add', table='adopter'))
		logged_in[0] = user.id
		logged_in[1] = user.name
		return redirect (url_for('homePage'))

	# if not logged in, check for username and password
	if login_id == 'unknown':
		output = '<form action="" method="POST">'
		output += '<input type="text" name="name" placeholder="Username"><br>'
		output += '<input type="text" name="pwd" placeholder="password"><br>'
		output += '<input type="submit" value="Login"> / <a href="%s">new user</a>'%(url_for('add',table='adopter'))
		output += '</form>'
		return render_template('main.php', login=logged_in, content=output)
	# if logged in, click name to update your profile
	else:
		return redirect (url_for('adopter',adopter_id=login_id))


# browse all puppies
@app.route('/puppies/')
def puppies():
	puppies = session.query(Puppy).all()
	pictures = session.query(Profile.picture).all()
	output = '<p><a href="%s">+ add a puppy</a></p>'%(url_for('add',table='puppy'))
	for p in puppies:
		output += '<p>'
		output += '<h2><a href="/puppy/%s">%s</a></h2> <br><img src="%s" alt="puppy picture for %s" style="width: 25vw">'%(p.id,p.name,session.query(Profile).filter_by(id=p.id)[0].picture,p.name)
		output += '<br><a href="%s">edit</a> &nbsp; &nbsp;'%(url_for('edit',table='puppy',index=p.id))
		output += '<a href="%s">delete</a>'%(url_for('delete',table='puppy',index=p.id))
		output += '</p>'
	
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

	shelters = session.query(Shelter).all()
	output = '<p><a href="%s">+ add a shelter</a></p>'%(url_for('add',table='shelter'))
	output += '<p><form action="" method="POST"><input type="submit" value="Rebalance Puppies!"></form></p>'
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
			session.commit()
			flash("Thank you for adopting a puppy! Click your profile to see all your puppies.")
		return redirect (url_for('homePage'))

	# get the puppy and associated profile
	puppy = session.query(Puppy).filter_by(id=puppy_id).first()
	profile = session.query(Profile).filter_by(id=puppy_id).first()
	shelter = session.query(Shelter).filter_by(id=puppy.shelter_id).first()
	# read puppy info to user
	output = '<h2>%s</h2>\
				<p><a href ="%s">edit</a></p>\
				<img src="%s">\
				<ul><li>Breed: %s</li>\
				<li>Home shelter: <a href="%s">%s</a></li>\
				<li>Gender: %s</li>\
				<li>Date of birth: %s</li>\
				<li>Weight: %s</li>\
				<li>Left ear: sloppy</li>\
				<li>Right ear: blopsy</li></ul>'%(puppy.name, url_for('edit',table='puppy',index=puppy_id), profile.picture, profile.breed, url_for('shelter',shelter_id=shelter.id), shelter.name, profile.gender, profile.dateOfBirth, profile.weight)
	
	# button for adopting this puppy if not already adopted
	if session.query(Adopter).filter_by(puppy_id=puppy_id).first() == None:
		output += '<p><form action="" method="POST"><input type="submit" value="Adopt me!"></form></p>'
	else:
		output += '<p><em>Someone adopted me! I have a home now!</em></p>'
	
	return render_template('main.php', login=logged_in, content=output)


# select specific shelter profile
@app.route('/shelter/<int:shelter_id>/')
def shelter(shelter_id):
	# get the puppy and associated profile
	shelter = session.query(Shelter).filter_by(id=shelter_id).first()
	output = '<h2>%s</h2>\
			   <p>%s<br>%s, %s %s<br><a href="http://%s">%s</a></p>'%(shelter.name, shelter.address, shelter.city, shelter.state, shelter.zipCode, shelter.website, shelter.website)
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

	if request.method=='POST':

		# check if any input fields are empty - send user back to this page
		for i in request.form:
			if request.form[i] == '' or request.form[i] == None:
				return redirect (url_for ('add', table=table))

		# add row to shelter table
		if table == 'shelter':
			new_row = Shelter (name=request.form['name'], address=request.form['address'], city=request.form['city'], zipCode=request.form['zipcode'], state=request.form['state'], website=request.form['website'], capacity=request.form['capacity'])
		
		# add row to adopter table
		elif table == 'adopter':
			new_row = Adopter (name=request.form['name'], address=request.form['address'], city=request.form['city'], zipCode=request.form['zipcode'], state=request.form['state'], website=request.form['website'], email=request.form['email'], password=request.form['pwd'])
		
		# add row to puppy table
		elif table == 'puppy':
			# try checking puppy in to shelter if shelter not full
			new_row = Puppy (name=request.form['name'], shelter_id=request.form['shelterID'])
			if session.query(Shelter).filter_by(id=new_row.shelter_id)[0].occupancy >= session.query(Shelter).filter_by(id=new_row.shelter_id)[0].capacity:
				# HOMELESS! - we can't place the puppy!
				new_row.shelter_id = None
				flash("Unable to place puppy - currently has no home shelter!")
			# create profile entry for this puppy too
			new_profile = Profile (puppy_id=new_row.id, breed=request.form['breed'], gender=request.form['gender'], weight=request.form['weight'], picture=request.form['picture'])
			session.add (new_profile)
		
		# found no table for this url variable
		else:
			return redirect (url_for ('homePage'))

		# add whichever row was created above to the db
		session.add (new_row)
		session.commit()
		# update shelter totals
		curate_shelter_capacity()
		# go home
		return redirect (url_for('homePage'))

	# if method is GET display form for user input
	output = '<form action="" method="POST">'
	
	# check which table user is adding to, then build form for that table
	if table == 'shelter':
		output += '<h2>Add one shelter!</h2>'
		output += 'Name: <input type="text" name="name"><br>\
		Address: <input type="text" name="address"><br>\
		City: <input type="text" name="city"><br>\
		Zip: <input type="text" name="zipcode"><br>\
		State: <input type="text" name="state"><br>\
		Website: <input type="text" name="website"><br>\
		Capacity: <input type="text" name="capacity"><br>'

	elif table == 'adopter':
		output += '<h2>Become an adopter!</h2>'
		output += 'User: <input type="text" name="name"><br>'
		output += 'Address: <input type="text" name="address"><br>'
		output += 'City: <input type="text" name="city"><br>'
		output += 'State: <input type="text" name="state"><br>'
		output += 'Zip: <input type="text" name="zipcode"><br>'
		output += 'Website: <input type="text" name="website"><br>'
		output += 'Email: <input type="text" name="email"><br>'
		output += 'Password: <input type="text" name="pwd"><br>'

	elif table == 'puppy':
		output += '<h2>Add one puppy!</h2>'
		output += '<p>Name: <input type="text" name="name"><br>\
		Breed: <input type="text" name="breed"><br>\
		Gender: <input type="radio" name="gender" value="male"> M <input type="radio" name="gender" value="female"> F<br>\
		Weight: <input type="text" name="weight"><br>\
		Date of birth: <input type="text" name="dateOfBirth"><br>\
		Picture: <input type="text" name="picture"></p>\
		Choose a Home Shelter for this puppy: <br>'
		# radio button select from existing shelters
		shelters = session.query(Shelter).all()
		for s in shelters:
			output += '<input type="radio" name="shelterID" value="%s"> %s<br>'%(s.id, s.name)

	# found no such table for this url var
	else:
		return redirect (url_for ('homePage'))
	
	# end form and page - submit to reach POST branch above
	output += '<p><input type="submit" value="Add"></p></form>'

	return render_template('main.php', login=logged_in, content=output)


# update a puppy, shelter or adopter in a table
@app.route('/edit/<table>/<int:index>/', methods=['GET','POST'])
def edit (table, index):

	if request.method=='POST':

		# check if any input fields are empty - send user back to this page
		for i in request.form:
			if request.form[i] == '' or request.form[i] == None:
				return redirect (url_for ('edit', table=table, index=index))

		# add row to shelter table
		if table == 'shelter':
			mod_row = session.query(Shelter).filter_by(id=index)[0]
			mod_row.name = request.form['name']
			mod_row.address = request.form['address']
			mod_row.city = request.form['city']
			mod_row.zipCode = request.form['zipcode']
			mod_row.state = request.form['state']
			mod_row.website = request.form['website']
			mod_row.capacity = request.form['capacity']
		
		# add row to adopter table
		elif table == 'adopter':
			mod_row = session.query(Adopter).filter_by(id=index)[0]
			mod_row.name = request.form['name']
			mod_row.address = request.form['address']
			mod_row.city = request.form['city']
			mod_row.zipCode = request.form['zipcode']
			mod_row.state = request.form['state']
			mod_row.email = request.form['email']
			mod_row.website = request.form['website']
			mod_row.password = request.form['password']
		
		# add row to puppy table
		elif table == 'puppy':
			mod_row = session.query(Puppy).filter_by(id=index)[0]
			mod_row.name = request.form['name']
			last_id = mod_row.shelter_id	# store current shelter in case new one is full
			mod_row.shelter_id = request.form['shelterID']
			mod_profile = session.query(Profile).filter_by(id=index)[0]
			mod_profile.breed = request.form['breed']
			mod_profile.gender = request.form['gender']
			mod_profile.weight = request.form['weight']
			mod_profile.picture = request.form['picture']
			session.add (mod_profile)
			# catch overflow puppies and unassign from full shelter
			if session.query(Shelter).filter_by(id=mod_row.shelter_id)[0].occupancy >= session.query(Shelter).filter_by(id=mod_row.shelter_id)[0].capacity:
				# shelter full - move to previous shelter
				flash("Shelter full! Unable to move puppy - staying in current home shelter!")
				mod_row.shelter_id = last_id				

		# found no table corresponding to url var - return home instead
		else:
			return redirect(url_for('homePage'))

		# edit row updated above in the db
		session.add (mod_row)
		session.commit()
		# update shelter totals
		curate_shelter_capacity()
		return redirect (url_for('homePage'))

	# if method is GET display form for user input
	output = '<form action="" method="POST">'
	
	# check which table user is adding to, then display inputs for that table
	if table == 'shelter':
		# read and display data for this shelter
		s = session.query(Shelter).filter_by(id=index)[0]
		output += '<h2>Edit this shelter!</h2>'
		output += 'Name: <input type="text" name="name" value="%s"><br>\
		Address: <input type="text" name="address" value="%s"><br>\
		City: <input type="text" name="city" value="%s"><br>\
		Zip: <input type="text" name="zipcode" value="%s"><br>\
		State: <input type="text" name="state" value="%s"><br>\
		Website: <input type="text" name="website" value="%s"><br>\
		Capacity: <input type="text" name="capacity" value="%s"><br>'%(s.name,s.address,s.city,s.zipCode,s.state,s.website,s.capacity)

	# read and display data for this adopter
	elif table == 'adopter':
		a = session.query(Adopter).filter_by(id=index)[0]
		output += '<h2>Edit this adopter!</h2>'
		output += 'Name: <input type="text" name="name" value="%s"><br>\
				   Address: <input type="text" name="address" value="%s"><br>\
				   City: <input type="text" name="city" value="%s"><br>\
				   State: <input type="text" name="state" value="%s"><br>\
				   Zip: <input type="text" name="zipcode" value="%s"><br>\
				   Email: <input type="text" name="email" value="%s"><br>\
				   Website: <input type="text" name="website" value="%s"><br>\
				   Password: <input type="text" name="password"><br>'%(a.name, a.address, a.city, a.state, a.zipCode, a.email, a.website)
	
	# read and display puppy and profile info
	elif table == 'puppy':
		p = session.query(Puppy).filter_by(id=index)[0]
		q = session.query(Profile).filter_by(id=index)[0]
		output += '<h2>Edit this puppy!</h2>'
		output += '<p>Name: <input type="text" name="name" value="%s"><br>\
		Breed: <input type="text" name="breed" value="%s"><br>'%(p.name,q.breed)
		# set the radio button for current profile gender as selected
		if (q.gender == 'male'):
			output += 'Gender: <input type="radio" name="gender" value="male" checked> M <input type="radio" name="gender" value="female"> F<br>'
		else:
			output += 'Gender: <input type="radio" name="gender" value="male"> M <input type="radio" name="gender" value="female" checked> F<br>'
		# read and display profile
		output += 'Weight: <input type="text" name="weight" value="%s"><br>\
		Date of birth: <input type="text" name="dateOfBirth" value="%s"><br>\
		Picture: <input type="text" name="picture" value="%s"></p>\
		Choose a Home Shelter for this puppy: <br>'%(q.weight,q.dateOfBirth,q.picture)
		# select from existing shelters
		shelters = session.query(Shelter).all()
		for s in shelters:
			if (s.id == p.shelter_id):
				output += '<input type="radio" name="shelterID" value="%s" checked>'%s.id
			else:
				output += '<input type="radio" name="shelterID" value="%s">'%s.id
			output += ' &nbsp;%s<br>'%s.name

	# found no table for this url variable - return home instead
	else:
		return redirect (url_for('homePage'))

	# end form and page - submit to reach POST branch above
	output += '<p><input type="submit" value="Modify"></p></form>'

	return render_template('main.php', login=logged_in, content=output)


# delete a Shelter, Puppy (including Profile) or Adopter from a table
@app.route('/delete/<table>/<int:index>/', methods=['GET','POST'])
def delete (table, index):

	if request.method=='POST':

		# check if any input fields are empty - send user back to this page
		for i in request.form:
			if request.form[i] == '' or request.form[i] == None:
				return redirect (url_for ('add', table=table))

		# delete row from shelter table
		if table == 'shelter':
			this_entry = session.query(Shelter).filter_by(id=index)[0]
		
		# delete row from adopter table
		elif table == 'adopter':
			this_entry = session.query(Adopter).filter_by(id=index)[0]
		
		# delete row from puppy and profile tables
		elif table == 'puppy':
			this_entry = session.query(Puppy).filter_by(id=index)[0]
			this_profile = session.query(Profile).filter_by(id=index)[0]
			session.delete (this_profile)

		# url variables matched no table - redirect
		else:
			return redirect (url_for ('homePage'))

		# edit row updated above in the db
		session.delete (this_entry)
		session.commit()
		# update shelter totals
		curate_shelter_capacity()
		return redirect (url_for('homePage'))

	# if method is GET display form for user to confirm the delete
	output = '<form action="" method="POST">'
	
	# check which table user is deleting from and display warning
	if table == 'shelter':
		s = session.query(Shelter).filter_by(id=index)[0]
		output += '<h2>Are you sure you want to delete %s?</h2>'%(s.name)
	elif table == 'adopter':
		a = session.query(Adopter).filter_by(id=index)[0]
		output += '<h2>Are you sure you want to delete %s?</h2>'%(a.name)
	elif table == 'puppy':
		p = session.query(Puppy).filter_by(id=index)[0]
		output += '<h2>Are you sure you want to delete %s?</h2>'%(p.name)
	# url variable does not relate to a table - return home instead
	else:
		return redirect (url_for('homePage'))
	# end form and page - submit to reach POST branch above
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
if __name__ == '__main__':
	# reload server every time notice code change
	app.debug = True
	# session secret key for message flashing
	app.secret_key = 'super_secret_key'
	# for accessing and running on vagrant
	app.run(host = '0.0.0.0', port = 5000)