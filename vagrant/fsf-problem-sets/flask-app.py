# basic flask stuff
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask (__name__)

# sqlalchemy stuff
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# setup connection for restaurant db
from puppies_db_setup import Base,Shelter,Puppy,Adopter,Profile
engine = create_engine ('sqlite:///puppies.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# visit root or select browse all puppies
@app.route('/')
def homePage():
	puppies = session.query(Puppy).all()
	pictures = session.query(Profile.picture).all()
	output = '<html><body><h1>FluppyBase</h1>'
	output += '<a href="/shelters/">Search by Shelter</a></p>'
	for p in puppies:
		output += '<p>'
		output += '<h2><a href="/puppy/%s">%s</a></h2> <br><img src="%s" alt="puppy picture for %s" style="width: 25vw">'%(p.id,p.name,session.query(Profile).filter_by(id=p.id)[0].picture,p.name)
		output += '<br><a href="%s">edit</a> &nbsp; &nbsp;'%(url_for('edit',table='puppy',index=p.id))
		output += '<a href="%s">delete</a>'%(url_for('delete',table='puppy',index=p.id))
		output += '</p>'
	output += '</body></html>'
	return output


# browse all shelters
@app.route('/shelters/')
def shelters():
	shelters = session.query(Shelter).all()
	output = '<html><body><h1>FluppyBase</h1>'
	output += '<a href="%s">Search by Puppy</a></p>'%(url_for('homePage'))
	for s in shelters:
		output += '<h2><a href="/shelter/%s">%s</a></h2>'%(s.id,s.name)
		output += '<br><a href="%s">edit</a> &nbsp; &nbsp;'%(url_for('edit',table='shelter',index=s.id))
		output += '<a href="%s">delete</a>'%(url_for('delete',table='shelter',index=s.id))
	output += '</body></html>'
	return output


# select specific puppy profile
@app.route('/puppy/<int:puppy_id>/')
def puppy(puppy_id):
	# get the puppy and associated profile
	puppy = session.query(Puppy).filter_by(id=puppy_id).first()
	profile = session.query(Profile).filter_by(id=puppy_id).first()
	output = '<html><body><h1>FluppyBase</h1>'
	output += '<a href="%s">Back to All Puppies</a></p>'%(url_for('homePage'))
	output += '<h2>%s</h2><img src="%s">\
					<ul><li>Breed: %s</li>\
					<li>Gender: %s</li>\
					<li>Date of birth: %s</li>\
					<li>Weight: %s</li>\
					<li>Left ear: sloppy</li>\
					<li>Right ear: blopsy</li></ul>'%(puppy.name, profile.picture, profile.breed, profile.gender, profile.dateOfBirth, profile.weight)
	output += '</body></html>'
	return output


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
			new_row = Adopter (name=request.form['name'])
		
		# add row to puppy table
		elif table == 'puppy':
			new_row = Puppy (name=request.form['name'], shelter_id=request.form['shelterID'])
			new_profile = Profile (puppy_id=new_row.id, breed=request.form['breed'], gender=request.form['gender'], weight=request.form['weight'], picture=request.form['picture'])
			session.add (new_profile)
		
		# found no table for this url variable
		else:
			return redirect (url_for ('homePage'))

		# add whichever row was created above to the db
		session.add (new_row)
		session.commit()
		# go home
		return redirect (url_for('homePage'))

	# if method is GET display form for user input
	output = '<html><body><h1>FluppyBase</h1>'
	output += '<a href="%s">Back to Puppies</a> &nbsp; <a href="%s">Back to Shelters</a></p>'%(url_for('homePage'), url_for('shelters'))
	output += '<form action="" method="POST">'
	
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
		output += '<h2>Add one adopter!</h2>'
		output += 'Name: <input type="text" name="name"><br>'

	elif table == 'puppy':
		output += '<h2>Add one puppy!</h2>'
		output += '<p>Name: <input type="text" name="name"><br>\
		Breed: <input type="text" name="breed"><br>\
		Gender: <input type="radio" name="gender" value="male"> M <input type="radio" name="gender" value="female"> F<br>\
		Weight: <input type="text" name="weight"><br>\
		Date of birth: <input type="text" name="dateOfBirth"><br>\
		Picture: <input type="text" name="picture"></p>\
		Choose a Home Shelter for this puppy: <br>'
		# select from existing shelters
		shelters = session.query(Shelter).all()
		for s in shelters:
			output += '<input type="radio" name="shelterID" value="%s">'%s.id
			output += ' &nbsp;%s<br>'%s.name

	# found no such table for this url var
	else:
		return redirect (url_for ('homePage'))
	
	# end form and page - submit to reach POST branch above
	output += '<p><input type="submit" value="Add"></p></form></body></html>'
	return output


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
		
		# add row to puppy table
		elif table == 'puppy':
			mod_row = session.query(Puppy).filter_by(id=index)[0]
			mod_row.name = request.form['name']
			mod_row.shelter_id = request.form['shelterID']
			mod_profile = session.query(Profile).filter_by(id=index)[0]
			mod_profile.breed = request.form['breed']
			mod_profile.gender = request.form['gender']
			mod_profile.weight = request.form['weight']
			mod_profile.picture = request.form['picture']
			session.add (mod_profile)

		# found no table corresponding to url var - return home instead
		else:
			return redirect(url_for('homePage'))

		# edit row updated above in the db
		session.add (mod_row)
		session.commit()
		return redirect (url_for('homePage'))

	# if method is GET display form for user input
	output = '<html><body><h1>FluppyBase</h1>'
	output += '<a href="%s">Back to Puppies</a> &nbsp; <a href="%s">Back to Shelters</a></p>'%(url_for('homePage'), url_for('shelters'))
	output += '<form action="" method="POST">'
	
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
		output += 'Name: <input type="text" name="name" value="%s"><br>'%(a.name)
	
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
	output += '<p><input type="submit" value="Modify"></p></form></body></html>'
	return output

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
		return redirect (url_for('homePage'))

	# if method is GET display form for user to confirm the delete
	output = '<html><body><h1>FluppyBase</h1>'
	output += '<a href="%s">Back to All Puppies</a></p>'%(url_for('homePage'))
	output += '<form action="" method="POST">'
	
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
			   <p><input type="submit" value="Delete"></p></form></body></html>'
	return output




# create new menu item for restaurant with this id
@app.route('/restaurant/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
	# catch form POST method at this URL (form method from GET template below)
	if request.method=='POST':
		# create a new menu item associated with this restaurant and add it to the db
		new_item = MenuItem (name=request.form['item_name'], restaurant_id=restaurant_id)
		session.add (new_item)
		session.commit()
		# message flashing
		flash("You just created a new menu item!")
		# redirect to the restaurant menu route
		return redirect (url_for('restaurantMenu',restaurant_id=restaurant_id))
	# GET requests go to template form for adding an item to this restaurant
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id)[0]
	return render_template ('new.html',restaurant=restaurant)


# edit an existing menu item after clicking on edit href in restaurantMenu template
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
	# catch form POST method at this URL (form method from GET template below)
	if request.method=='POST':
		# create a new menu item associated with this restaurant and add it to the db
		mod_item = session.query(MenuItem).filter_by(id=menu_id)[0]
		mod_item.name = request.form['item_name']
		session.add (mod_item)
		session.commit()
		# message flashing
		flash ("You just edited an item!")
		# redirect to the restaurant menu route
		return redirect (url_for('restaurantMenu',restaurant_id=restaurant_id))
	# GET requests go to template form for adding an item to this restaurant
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id)[0]
	item = session.query(MenuItem).filter_by(id=menu_id)[0]
	return render_template ('edit.html',restaurant=restaurant,item=item)


# delete an existing menu item after clicking on delete href in restaurantMenu template
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
	# catch form POST method at this URL (form method from GET template below)
	if request.method=='POST':
		# create a new menu item associated with this restaurant and add it to the db
		this_item = session.query(MenuItem).filter_by(id=menu_id)[0]
		session.delete (this_item)
		session.commit()
		# message flashing
		flash ("You just deleted an item!")
		# redirect to the restaurant menu route
		return redirect (url_for('restaurantMenu',restaurant_id=restaurant_id))
	# GET requests go to template form for adding an item to this restaurant
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id)[0]
	item = session.query(MenuItem).filter_by(id=menu_id)[0]
	return render_template ('delete.html',restaurant=restaurant,item=item)


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