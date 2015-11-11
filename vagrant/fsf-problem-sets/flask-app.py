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
		output += '<p><a href="/puppy/%s">%s</a> <br><img src="%s" alt="puppy picture for %s" style="width: 25vw"></p>'%(p.id,p.name,pictures[p.id-1][0],p.name)
	output += '</body></html>'
	return output

# browse all shelters
@app.route('/shelters/')
def shelters():
	shelters = session.query(Shelter).all()
	output = '<html><body><h1>FluppyBase</h1>'
	output += '<a href="%s">Search by Puppy</a></p>'%(url_for('homePage'))
	for s in shelters:
		output += '<p><a href="/shelter/%s">%s</a></p>'%(s.id,s.name)
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
					<ul><li>Gender: %s</li>\
					<li>Date of birth: %s</li>\
					<li>Left ear: sloppy</li>\
					<li>Right ear: blopsy</li></ul>'%(puppy.name, profile.picture, profile.gender, profile.dateOfBirth)
	output += '</body></html>'
	return output

# select specific puppy profile
@app.route('/add/<int:table>/', methods=['GET','POST'])
def add (table):

	if request.method=='POST':

		# check if any input fields are empty - send user back to this page
		for i in request.form:
			if request.form[i] == '' or request.form[i] == None:
				return redirect (url_for ('add', table=table))

		# add row to shelter table
		if table == 0:
			new_row = Shelter (name=request.form['name'], address=request.form['address'], city=request.form['city'], zipCode=request.form['zipcode'], state=request.form['state'], website=request.form['website'], capacity=request.form['capacity'])
		
		# add row to adopter table
		elif table == 1:
			new_row = Adopter (name=request.form['name'])
		
		# add row to puppy table
		else:
			new_row = Puppy (name=request.form['name'], shelter_id=request.form['shelterID'])
			new_profile = Profile (puppy_id=new_row.id, breed=request.form['breed'], gender=request.form['gender'], weight=request.form['weight'], picture=request.form['picture'])
			session.add (new_profile)

		session.add (new_row)
		session.commit()
		return redirect (url_for('homePage'))

	# if method is GET display form for user input
	output = '<html><body><h1>FluppyBase</h1>'
	output += '<a href="%s">Back to All Puppies</a></p>'%(url_for('homePage'))
	output += '<form action="" method="POST">'
	
	# check which table user is adding to, then display inputs for that table
	if table == 0:
		output += '<h2>Add one shelter!</h2>'
		output += 'Name: <input type="text" name="name"><br>\
		Address: <input type="text" name="address"><br>\
		City: <input type="text" name="city"><br>\
		Zip: <input type="text" name="zipcode"><br>\
		State: <input type="text" name="state"><br>\
		Website: <input type="text" name="website"><br>\
		Capacity: <input type="text" name="capacity"><br>'
	elif table == 1:
		output += '<h2>Add one adopter!</h2>'
		output += 'Name: <input type="text" name="name"><br>'
	else:
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
	# end form and page - submit to reach POST branch above
	output += '<p><input type="submit" value="Add"></p></form></body></html>'
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
@app.route('/restaurant/<int:restaurant_id>/JSON/')
def restaurantMenuJSON(restaurant_id):
	# query for appropriate items
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
	# rely on @property serialize for MenuItem class in ormtest.py
	return jsonify(MenuItems = [i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def restaurantMenuItemJSON(restaurant_id, menu_id):
	# query for this item
	item = session.query(MenuItem).filter_by(id=menu_id).one()
	# return @property serialize defined in ormtest.py as JSON
	return jsonify(MenuItem = [item.serialize])


# run if this is app but not if imported as module
if __name__ == '__main__':
	# reload server every time notice code change
	app.debug = True
	# session secret key for message flashing
	app.secret_key = 'super_secret_key'
	# for accessing and running on vagrant
	app.run(host = '0.0.0.0', port = 5000)