from foodbase import app

from flask import render_template, request, redirect, url_for, flash, jsonify

import math

# /!\ read up on json and requests - used here to handle API
import json, requests

# get my WTForms classes from forms.py
from forms import LoginForm, RestaurantForm, MenuItemForm

# sql functionality
from sqlalchemy import create_engine, func, distinct, asc, desc
from sqlalchemy.orm import sessionmaker

# set up connection for db
from models import Base,Restaurant,MenuItem
engine = create_engine ('sqlite:///foodbase/models.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def home():
	return redirect(url_for('restaurants'))


# read routes for restaurants and menu items
@app.route('/restaurants/') 							# view all restaurants
@app.route('/restaurants/<int:index>/')					# results broken into pages
@app.route('/restaurants/<int:page>/<int:per_page>')	# paginate results
@app.route('/restaurants/<int:index>/menu/') 			# view a restaurant menu
def restaurants (index=None, page=1, per_page=3, display_all=False):

	# add city variable for switching between markets
	user_city = 'Kona'

	# browse menu items for a single restaurant
	if index != None:
		r = session.query(Restaurant).filter_by(id=index)[0]
		m = session.query(MenuItem).filter_by(restaurant_id=index)
		o = '<p>%s - main menu</p>'%r.name
		o += '<ul>'
		for i in m:
			o += '<li>%s<br>%s<br><a href="%s">edit</a> <a href="%s">delete</a></li>'%(i.name,i.description,url_for('update',table='MenuItem',index=i.id),url_for('delete',table='MenuItem',index=i.id)) 
		o += '</ul>'
		o += '<p><a href="%s">+ new item</a></p>' % (url_for('add',table='MenuItem'))
	
	# browse all restaurants
	else:
		# Query and title
		restaurants = session.query(Restaurant).all()
		o = '%s'%'<h2>Our ring of restaurants</h2>'

		#
		# Display image grid
		#
		o += '<div class = "frontimgs">'
		# count through results and paginate based on current "page"
		per_row = 4
		count = 0
		for r in restaurants:
			# use counter to show only results between page start and page end
			current_results = 0 	# number of results being displayed this page load
			if display_all == False and count >= (per_page*page-per_page) and count < (per_page*page):
				current_results += 1
				# restaurant link and image
				o += '<div class="oneimg"><a href="%s"><img src="%s" alt="%s"></a>' % (url_for('restaurants', index=r.id), r.image, r.name)
				# restaurant crud operations
				o += '<br><a href="%s">edit</a> <a href="%s">delete</a></div>'%(url_for('update', table='Restaurant', index=r.id), url_for('delete', table='Restaurant', index=r.id))
				# break off a new row after a certain number of results
				if current_results % per_row == 0:
					o += '<br>'
			# display all restaurants (no pagination)
			if display_all == True:
				o += '<div class="oneimg"><a href="%s"><img src="%s" alt="%s"></a>' % (url_for('restaurants', index=r.id), r.image, r.name)
				# restaurant crud operations
				o += '<br><a href="%s">edit</a> <a href="%s">delete</a></div>'%(url_for('update', table='Restaurant', index=r.id), url_for('delete', table='Restaurant', index=r.id))
			# count up restaurant number	
			count += 1

		o += '</div><br><div>'
		#
		# Row of links to all paginated results
		# Display links for as many pages as count is divisible by paginator
		# 
		for p in range (0, int(math.ceil(count/per_page))+1):
			# build pagination link
			o += '&nbsp; <a href="%s">page %s</a> &nbsp;' % (url_for('restaurants', index=None, page=p+1, per_page=per_page), p+1)
		o += '<a href="%s">ALL</a></div>'%url_for('restaurants',index=None,page=p,per_page=per_page,display_all=True)

		#
		# Display text list of restaurants
		# 
		o += '<ul>'
		for r in restaurants:
			o += '<li><a href="%s">%s</a> <a href="%s">(edit)</a> <a href="%s">(delete)</a></li>' % (url_for('restaurants', index=r.id), r.name, url_for('update',table='Restaurant',index=r.id), url_for('delete',table='Restaurant',index=r.id))
		o += '</ul><p><a href="%s">+ new restaurant</a></p>'%url_for('add', table='Restaurant')
		# /!\ DANGEROUS database wipe option
		o += '<p><a href="%s">/!\\ Reset this APP /!\\</p>'%url_for('repopulateRelations',city_name=user_city)

	return render_template('main.php',content=o)


@app.route('/add/<table>/', methods=['GET','POST'])
def add(table):
	# get form template from WTForm class for this table
	form = RestaurantForm (request.form)
	if table == 'Restaurant':
		form = RestaurantForm(request.form)
	elif table == 'MenuItem':
		form = MenuItemForm(request.form)
	else:
		flash ('I didn\'t understand! Please try adding a /Restaurant/ or a /MenuItem/.')

	# POST add restaurant to database
	if request.method == 'POST' and form.validate():
		if table == 'Restaurant':
			new_row = Restaurant (name=form.name.data, address=form.address.data, city=form.city.data, state=form.state.data, zipCode=form.zipCode.data, website=form.website.data, cuisine=form.cuisine.data)
		elif table == 'MenuItem':
			new_row = MenuItem (name=form.name.data, description=form.description.data, restaurant_id=form.restaurant_id.data)
		else:
			flash ('Please try to add a /Restaurant/ or a /MenuItem/.')
		session.add (new_row)
		session.commit ()
		return redirect (url_for('home'))
		
	# GET display form for adding restaurant
	return render_template ('form.php', form=form, content='')


@app.route('/update/<table>/<int:index>/', methods=['GET','POST'])
def update(table,index):
	# retrieve form class from forms.py based on URL keyword
	if table == 'Restaurant':
		form = RestaurantForm (request.form)
	elif table == 'MenuItem':
		form = MenuItemForm (request.form)
	else:
		flash ('This isn\'t the /update/ you are looking for! We don\'t recognize that URL.')
		return redirect (url_for('home'))

	# POST edit database on form submission
	if request.method == 'POST':

		is_valid = form.validate() 	# store validation test result

		# make edits to a restaurant
		if table == 'Restaurant' and is_valid:
			mod_row = session.query(Restaurant).filter_by(id=index)[0]
			mod_row.name = form.name.data
			mod_row.cuisine = form.cuisine.data
			mod_row.address = form.address.data
			mod_row.city = form.city.data
			mod_row.state = form.state.data
			mod_row.zipCode = form.zipCode.data
			mod_row.website = form.website.data
			mod_row.image = form.image.data
			flash ('I updated the profile for %s!'%mod_row.name)

		# make edits to a menu item
		elif table == 'MenuItem' and is_valid:
			mod_row = session.query(MenuItem).filter_by(id=index)[0]
			mod_row.name = form.name.data
			mod_row.description = form.description.data
			mod_row.restaurant_id = form.restaurant_id.data

		# cannot update the table
		else:
			flash ('Help, I couldn\'t add that info to FoodBase! Do you mind checking if you filled out the whole form?')
			return redirect (url_for('update', table=table, index=index))

		# update table row in the db
		session.add (mod_row)
		session.commit()
		flash ('Successfully updated %s!'%mod_row.name)
		return redirect (url_for('home'))

	# GET - retrieve data and build the form
	if table == 'Restaurant':
		# if user requests update restaurant form
		r = session.query(Restaurant).filter_by(id=index)[0]
		form.name.data = r.name
		form.cuisine.data = r.cuisine
		form.address.data = r.address
		form.city.data = r.city
		form.state.data = r.state
		form.zipCode.data = r.zipCode
		form.website.data = r.website
		form.image.data = r.image
	elif table == 'MenuItem':
		m = session.query(MenuItem).filter_by(id=index)[0]
		form.name.data = m.name
		form.description.data = m.description
		form.restaurant_id.data = m.restaurant_id
	else:
		# if user requests other update forms
		flash ('I couldn\'t update that. Please try to update a /Restaurant or a /MenuItem instead!')
	return render_template('form.php', form=form, content='')


@app.route('/delete/<table>/<int:index>/', methods=['GET','POST'])
def delete(table,index):
	# retrieve form class from forms.py based on URL
	# delete a restaurant
	if table == 'Restaurant':
		mod_row = session.query(Restaurant).filter_by(id=index)[0]
	# delete a menu item
	elif table == 'MenuItem':
		mod_row = session.query(MenuItem).filter_by(id=index)[0]
	else:
		flash ('I couldn\'t delete that info from FoodBase!')
		return redirect (url_for('home'))

	# POST - delete from database on submission
	if request.method == 'POST':
		# delete selected row
		session.delete (mod_row)
		session.commit()
		flash ('I erased that information from FoodBase!')
		return redirect (url_for('home'))

	# GET - create page verifying the delete
	o = '<p>Do you really want to delete %s?</p>' % mod_row.name
	o += '<form action="" method="POST"><button>Delete!</button></form>'

	o += '<form action="%s" method="GET">\
		<button>No!</button></form>' % url_for('home')

	return render_template('main.php', content=o)

@app.route('/<table>/<int:index>/JSON/')
@app.route('/<table>/JSON/')
def json_api(table,index=None):
	if table == 'Restaurant' or table == 'restaurant':
		if index != None:
			data = session.query(Restaurant).filter_by(id=index).one()
			return jsonify(Restaurant = [data.serialize])
		else:
			data = session.query(Restaurant).all()
			return jsonify(Restaurants = [r.serialize for r in data])
	elif table == 'MenuItem' or table == 'menuitem':
		if index != None:
			data = session.query(MenuItem).filter_by(id=index).one()
			return jsonify(MenuItem = [data.serialize])
		else:
			data = session.query(MenuItem).all()
			return jsonify(MenuItems = [r.serialize for r in data])
	else:
		flash ('Could not find any FoodBase data matching your request!')
		return redirect (url_for('home'))


@app.route('/repopulateRelations/<city_name>',methods=['GET','POST'])
def repopulateRelations(city_name):

	if request.method == 'POST':
		
		# clean out current items in db
		session.query(Restaurant).delete()
		session.query(MenuItem).delete()

		# grab data from API
		jsonRestaurants = requests.get ('http://opentable.herokuapp.com/api/restaurants?city=%s'%city_name)
		jsonRestaurants = json.loads (jsonRestaurants.text)
		restaurant_list = jsonRestaurants['restaurants']

		# create new restaurant objects and add to relation 
		for r in restaurant_list:
			new_r = Restaurant(name=r['name'], address=r['address'], city=r['city'],state=r['state'], zipCode=r['postal_code'], website=r['reserve_url'], image=r['image_url'])
			session.add (new_r)

		session.commit()
		flash('You successfully wiped and repopulated FoodBase')
		return redirect (url_for('home'))

	# GET - warn that user is about to reset the whole db
	else:
		o = 'You are about to reset our entire database! Are you MAD?!?'
		o += '<form action="" method="POST">\
			  <button>Yes</button></form>'
		o += '<p><a href="%s">Not yet.</a></p>'%url_for('home')
	return render_template('main.php',content=o)