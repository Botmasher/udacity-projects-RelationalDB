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

# target market with null initial value
user_city = None


@app.route('/', methods=['GET','POST'])
def home():
	# change city request is sent here
	if request.method == 'POST':
		global user_city 		# reference to the global variable
		# pick out the market name from form built in select-market.js
		user_city = request.form['market-name']
		# go to post method for API call to restaurants JSON and rebuild db
		return redirect(url_for('repopulateRelations'), code=307)
	
	# just send to main restaurants list
	return redirect(url_for('restaurants'))


# read routes for restaurants and menu items
@app.route('/restaurants/') 						# view all restaurants
@app.route('/restaurants/<int:index>/')				# results broken into pages
@app.route('/restaurants/<int:page>/<int:per_pg>/')	# paginate results
@app.route('/restaurants/<int:index>/menu/') 		# view a restaurant menu
def restaurants (index=None, page=1, per_pg=5):

	# set a default city market for testing
	global user_city 		# reference to the global variable

	if user_city == None:
		# currently sets the city to market in db (last selected)
		# BUILD: get market based on user location
		if session.query(Restaurant).first() != None:
			user_city = session.query(Restaurant).first().city
		# set a default city for cases where db is empty
		else:
			user_city = 'Your City!'

	# output text that will be filled in and added to template content
	o = ''

	# browse menu items for a single restaurant
	if index != None:
		r = session.query(Restaurant).filter_by(id=index)[0]
		m = session.query(MenuItem).filter_by(restaurant_id=index)
		o += '<p>%s - main menu</p>'%r.name
		o += '<ul>'
		for i in m:
			o += '<li>%s<br>%s<br><a href="%s">edit</a> <a href="%s">delete</a></li>'%(i.name,i.description,url_for('update',table='MenuItem',index=i.id),url_for('delete',table='MenuItem',index=i.id)) 
		o += '</ul>'
		o += '<p><a href="%s">+ new item</a></p>' % (url_for('add',table='MenuItem'))
	
	# browse all restaurants
	else:
		# Query for restaurants
		restaurants = session.query(Restaurant).all()

		#
		# Build image grid
		#

		# use counter to show only results between page start and page end
		count = 0
		# remember results to print to webpage
		results_store = {}

		for r in restaurants:
			# count up restaurant number to compare for pagination
			count += 1
			# count through and remember results based on pagination variables
			if count >= ((per_pg * page)-per_pg) and count <= (per_pg*page):
				results_store[r.id] = [r.name, r.image]
			# display all restaurants without calculating pagination
			elif per_pg == 0 and page == 0:
				results_store[r.id] = [r.name, r.image]
			# do not remember this restaurant (complement to first branch)
			else:
				pass

		# display image and crud links for each restaurant
		grid = ''
		for r_id in results_store:
			# display restaurant image and restaurant name with link
			grid += '<div class ="oneimg">'
			grid += '<a href="%s"><h3>%s</h3><img src="%s" alt="%s"></a>'	\
				 	% (url_for('restaurants', index=r_id), results_store[r_id][0][:16]+'...', results_store[r_id][1], results_store[r_id][0])
			grid += '<br>'
			# display and format update and delete links
			grid += '<a href="%s">edit</a> &nbsp;&nbsp; ' 	\
				 	% (url_for('update', table='Restaurant', index=r_id))
			grid += '<a href="%s">delete</a>' 				\
					% (url_for('delete', table='Restaurant', index=r_id))
			grid += '</div>'	# end single image (class "oneimg")

		#
		# Build row of links to all paginated results
		# 
		pagination = '<div class = "pagination-links">'
		number_of_pages = 0
		if per_pg > 0:
			# display links for as many pages as count is divisible by paginator
			for p in range (0, int(math.ceil(count/per_pg))+1):
				
				# keep track of how many pages we have
				number_of_pages += 1

				# build pagination link
				
				## Ajax loadentries loaded from /static/loadentries.js
				pagination += '&nbsp; <a href="" class="loadentries" name="%s-%s">Page %s</a> &nbsp;' % (p+1, per_pg, p+1)
			
			# buid link for displaying all restaurants without pagination
			pagination += '<a href="%s">View all</a></div>' % url_for('restaurants',index=None,page=0,per_pg=0)
		else:
			# displaying all results
			# build link for returning to default - pagination
			pagination += '<a href="%s">Break results into pages</a></div>' % url_for('restaurants')


		##
		## Display Image Grid and Pagination (both calculated and built above)
		##

		# place image grid on page with fwd and back arrows
		o += '<a href="%s" class="arrow-links"><div class = "grid-arrow"><div class = "left">&lt;</div></div></a>' % url_for('restaurants', page=max(page-1,1), per_pg=per_pg)
		o += '<div class = "frontimgs">%s</div>' % grid
		o += '<a href="%s" class="arrow-links"><div class = "grid-arrow"><div class = "right">&gt;</div></div></a>' % url_for('restaurants', page=min(page+1,number_of_pages), per_pg=per_pg)

		# add pagination links below the grid
		o += pagination


		# #
		# # Display plain text list of restaurant names with links
		# #
		# o += '<ul>' # open restaurant list
		
		# for r in restaurants:
		# 	o += '<li><a href="%s">%s</a> <a href="%s">(edit)</a> <a href="%s">(delete)</a></li>' % (url_for('restaurants', index=r.id), r.name, url_for('update',table='Restaurant',index=r.id), url_for('delete',table='Restaurant',index=r.id))
		# o += '</ul>' # close restaurant list

		# /!\ CAUTION allow adding a restaurant to the db
		o += '<br><p><a href="%s">+ new restaurant</a></p>'%url_for('add', table='Restaurant')

	return render_template('main.php',market=user_city, content=o)


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
	return render_template ('form.php', market=user_city, form=form, content='')


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
	return render_template('form.php', market=user_city, form=form, content='')


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

	return render_template('main.php', market=user_city, content=o)


@app.route('/<table>/<int:index>/JSON/')
@app.route('/<table>/JSON/')
def json_api(table,index=None):
	# serialize JSON results for requested entities
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


@app.route('/repopulateRelations/',methods=['GET','POST'])
def repopulateRelations():
	'''Replace all data in the database with restaurants from the requested city'''
	# reference to city market
	global user_city

	if request.method == 'POST':

		# grab data from API for this market
		jsonRestaurants = requests.get ('http://opentable.herokuapp.com/api/restaurants?city=%s'%user_city)
		jsonRestaurants = json.loads (jsonRestaurants.text)
		restaurant_list = jsonRestaurants['restaurants']

		# do not update the db if API has no results for this market
		if len(restaurant_list) < 1:
			# reset user city back to previous value
			user_city = None

		# reset db with restaurants for this market
		else:
			# clean out current items in db
			session.query(Restaurant).delete()
			session.query(MenuItem).delete()

			# iterate through restaurants and add to db
			for r in restaurant_list:
				new_r = Restaurant(name=r['name'], address=r['address'], city=r['city'],state=r['state'], zipCode=r['postal_code'], website=r['reserve_url'], image=r['image_url'])
				session.add (new_r)

			session.commit()

		return redirect (url_for('home'))

	# GET - warn that user is about to reset the whole db
	else:
		o = 'You are about to reset our entire database! Are you MAD?!?'
		o += '<form action="" method="POST">\
			  <button>Yes</button></form>'
		o += '<p><a href="%s">Not yet.</a></p>'%url_for('home')
	return render_template('main.php', market=user_city, content=o)