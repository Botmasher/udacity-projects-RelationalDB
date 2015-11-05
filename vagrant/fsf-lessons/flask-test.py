# basic flask stuff
from flask import Flask, render_template, request, redirect, url_for, flash
app = Flask (__name__)

# sqlalchemy stuff
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# setup connection for restaurant db
from ormtest import Base,Restaurant,MenuItem
engine = create_engine ('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# mock up a little test database with my orm classes
menu_items = ['this pizza', 'that pizza', 'thother pizza', 'nuffies pizza']
menu_prices = [9.50, 8.99, 10.95, 7.00]
menu_desc = ['No man can has cheesier than this one. And that is the Germanic people manniz, meaning everyone.','That sauce is better with more sauce.', 'Finally... a pizza that takes being a pizza seriously.', 'You can\'t eat the void but you can pay for it.']
session.query(MenuItem).delete()
# refill tables
for x in range(0,len(menu_items)):
	new_item = MenuItem (name=menu_items[x], price=menu_prices[x], description=menu_desc[x], restaurant_id=1)
	session.add(new_item)
session.commit()					# persist the changes


# decorator functions to catch routes
@app.route('/')
@app.route('/restaurant/')
# if successfully route, execute this
def restaurants():
	restaurants = session.query(Restaurant).all()
	output = ''
	for r in restaurants:
		output += '<p><a href="/restaurant/%s">%s</a></p>'%(r.id,r.name)
	return output


# when user clicks on specific restaurant from root
@app.route('/restaurant/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
	# get the restaurant and associated menu items
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id)
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
	# return rendered page (/templates/menu.html) formatting the restaurant and its menu
	return render_template ('menu.html', restaurant=restaurant[0], items=items)


# create new menu item for restaurant with this id
@app.route('/restaurant/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
	# catch form POST method at this URL (form method from GET template below)
	if request.method=='POST':
		# create a new menu item associated with this restaurant and add it to the db
		new_item = MenuItem (name=request.form['item_name'], restaurant_id=restaurant_id)
		session.add (new_item)
		session.commit()
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
		# redirect to the restaurant menu route
		return redirect (url_for('restaurantMenu',restaurant_id=restaurant_id))
	# GET requests go to template form for adding an item to this restaurant
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id)[0]
	item = session.query(MenuItem).filter_by(id=menu_id)[0]
	return render_template ('delete.html',restaurant=restaurant,item=item)


# run if this is app but not if imported as module
if __name__ == '__main__':
	# reload server every time notice code change
	app.debug = True
	# for accessing and running on vagrant
	app.run(host = '0.0.0.0', port = 5000)