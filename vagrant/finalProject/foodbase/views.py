from foodbase import app

import math

# basic framework render, req handling, endpoints and messaging
from flask import render_template, request, redirect, url_for, flash, jsonify

# /!\ read up on json and requests (imported below) - used here to handle API
import json

# get my WTForms classes from forms.py
from forms import LoginForm, RestaurantForm, MenuItemForm

# added to support OAuth 2
from flask import session as login_session
import random, string
# see gconnect() below for example of these imports in action
# create flow obj from json client id, client secret and other OAuth2 params
from oauth2client.client import flow_from_clientsecrets
# method for errors when trying to exchange one-time code for authorization token
from oauth2client.client import FlowExchangeError
# comprehensive http client library in Python
# also import JSON for this - already done below for a separate task
import httplib2
# turn return val from function into a real response obj to send off to client
from flask import make_response
# Apache 2 licensed http lib similar to urllib but with improvements
import requests

# sql functionality
from sqlalchemy import create_engine, func, distinct, asc, desc
from sqlalchemy.orm import sessionmaker

# set up connection for db
from models import Base, Restaurant, MenuItem, User
#engine = create_engine ('sqlite:///foodbase/models.db')
# use new users db
engine = create_engine ('sqlite:///foodbase/modelswithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# load JSON file downloaded from console.developers.google.com
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

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
def restaurants (index=None, page=1, per_pg=4):

	# set a default city market for testing
	global user_city 		# reference to the global variable

	if user_city == None:
		# currently sets the city to market in db (last selected)
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
			if count >= ((per_pg * page)-per_pg + 1) and count <= (per_pg*page):
				results_store[r.id] = [r.name, r.image]
			# display all restaurants without calculating pagination
			elif per_pg == 0 and page == 0:
				results_store[r.id] = [r.name, r.image]
			# do not remember this restaurant (complement to first branch)
			else:
				pass

		# image and crud links for each restaurant
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
		
		# verify paginatability
		#  - return all results when results per page is 0 (treat as "infinite")
		#  - check that results are not 0 to avoid division and modulo errors
		if per_pg > 0:

			# calculate number of pages
			if count % per_pg > 0:
				number_of_pages = (count - (count % per_pg)) / per_pg
				number_of_pages += 1
			else:
				number_of_pages = count / per_pg
			# display links for as many pages as count is divisible by paginator
			for p in range (0, number_of_pages):

				# build pagination link
				
				## Ajax loadentries loaded from /static/loadentries.js
				pagination += '&nbsp; <a href="" class="loadentries" name="%s-%s">Page %s</a> &nbsp;' % (p+1, per_pg, p+1)
			
			# buid link for displaying all restaurants without pagination
			pagination += '<a href="%s">View all</a></div>' % url_for('restaurants',index=None,page=0,per_pg=0)
		else:
			# displaying all results
			# build link for returning to default - pagination
			pagination += '<a href="%s">Break results into pages</a></div>' % url_for('restaurants')

		#
		# Display Image Grid and Pagination (both calculated and built above)
		#

		# place image grid on page with fwd and back arrows
		o += '<a href="%s" class="arrow-links"><div class = "grid-arrow"><div class = "left">&lt;</div></div></a>' % url_for('restaurants', page=max(page-1,1), per_pg=per_pg)
		o += '<div class = "frontimgs">%s</div>' % grid
		o += '<a href="%s" class="arrow-links"><div class = "grid-arrow"><div class = "right">&gt;</div></div></a>' % url_for('restaurants', page=min(page+1,number_of_pages), per_pg=per_pg)

		# add pagination links below the grid
		o += pagination

		# /!\ CAUTION allow adding a restaurant to the db
		o += '<br><p><a href="%s">+ new restaurant</a></p>'%url_for('add', table='Restaurant')

	return render_template('main.php',market=user_city, content=o)


@app.route('/add/<table>/', methods=['GET','POST'])
def add(table):
	if 'username' not in login_session:
		return redirect('/login')

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
			new_row = Restaurant (name=form.name.data, user_id=login_session['user_id'], address=form.address.data, city=form.city.data, state=form.state.data, zipCode=form.zipCode.data, website=form.website.data, cuisine=form.cuisine.data)
			flash ('New restaurant created!')
		elif table == 'MenuItem':
			new_row = MenuItem (name=form.name.data, user_id=login_session['user_id'], description=form.description.data, restaurant_id=form.restaurant_id.data)
			flash ('New menu item created!')
		else:
			flash ('Please try to add a /Restaurant/ or a /MenuItem/.')
		session.add (new_row)
		session.commit ()
		return redirect (url_for('home'))
		
	# GET display form for adding restaurant
	return render_template ('form.php', market=user_city, form=form, content='')


@app.route('/update/<table>/<int:index>/', methods=['GET','POST'])
def update(table,index):
	if 'username' not in login_session:
		return redirect('/login')

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
	if 'username' not in login_session:
		return redirect('/login')

	# retrieve form class from forms.py based on URL
	# delete a restaurant
	if table == 'Restaurant':
		mod_row = session.query(Restaurant).filter_by(id=index)[0]
		flash ('Restaurant deleted!')
	# delete a menu item
	elif table == 'MenuItem':
		mod_row = session.query(MenuItem).filter_by(id=index)[0]
		flash ('Menu item deleted!')
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

		flash ('Successfully updated the database with entries from %s' % user_city)

		return redirect (url_for('home'))

	# GET - warn that user is about to reset the whole db
	else:
		o = 'You are about to reset our entire database! Are you MAD?!?'
		o += '<form action="" method="POST">\
			  <button>Yes</button></form>'
		o += '<p><a href="%s">Not yet.</a></p>'%url_for('home')
	return render_template('main.php', market=user_city, content=o)


# Generate Anti-Forgery State Token
# Added to handle OAuth 2 - new state val on each visit to login endpoint
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.php', state=login_session['state'])


# server-side route for getting G oauth2 token response
@app.route('/gconnect', methods=['POST'])
def gconnect():
	# verify that the user is the one making the request
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state token'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# collect the one-time code from our server
	code = request.data
	# upgrade the one-time code to a credentials object by exchanging it
	try:
		# will contain access token from our server
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)   # initiate exchange
	# handle errors along the flow exchange
	except:
		response = make_response(json.dumps('Failed to upgrade authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# if we got here, we have the credentials obj - check for valid access token
	access_token = credentials.access_token
	# let G verify if it's a valid token for use
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])

	# we do not have a working access token - send 500 error to client
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# we do not have the right access token (matching g id) - 401 error to client
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps('Token\'s user ID doesn\'t match given user ID.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# we do not have matching client id's - 401 error to client
	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps('Token\'s client ID does not match app\'s.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# check if user is already logged in
	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		# return success without resetting login vars again
		response = make_response(json.dumps('Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# login was valid - store the access token for later
	login_session['credentials'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# get more info about the user
	userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	# request the info allowed by my token's scope
	answer = requests.get(userinfo_url, params = params)
	data = json.loads(answer.text)  	# store the info

	# store the specific data our app is interested in
	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	# /!\ 500 ERROR - may need different scope to access email /!\
	#login_session['email'] = data['email']

	# simple response that shows we were able to use user info
	o = '<h1>Welcome, %s!</h1>' % login_session['username']
	o += '<img src = "%s"' % login_session['picture']
	o += ' style = "width: 200px; height: 200px; border-radius: 50px; -webkit-border-radius: 50px; -moz-border-radius: 50px;">'
	flash('You are now logged in as %s' % login_session['username'])
	return o


@app.route('/gdisconnect')
def gdisconnect():
	access_token = login_session.get('credentials')
	# we don't have record of a user that we can disconnect
	if access_token is None:
		response = make_response(json.dumps('Current user isn\'t connected.'), 401)
		response.headers['Content-Type'] = 'application/json; charset=utf-8'
		return response
	# pass access token to G url for revoking tokens
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	# hit url and store response in a results object
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	# successful response
	if result['status'] == '200':
		# reset our app login_session data
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		#del login_session['email']
		del login_session['picture']
		# pass client successful disconnect
		response = make_response(json.dumps('User successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json; charset=utf-8'
		return response
	# invalid token or somehow revoke not successful
	else:
		response = make_response(json.dumps('Failed to revoke token and disconnect.'), 400)
		response.headers['Content-Type'] = 'application/json; charset=utf-8'
		return response


# methods for handling User model once we get a user through OAuth
def createUser(login_session, auth_provider):
	if auth_provider == 'gplus':
		auth_id= login_session['gplus_id']
	else:
		# no recognized oauth provider given - unique user not created
		return None
	newUser = User(name=login_session['username'], auth_id=auth_id, auth_site=auth_provider, picture=login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(auth_id=auth_id, auth_site=auth_provider).one()
	return user.id

def getUserInfo (user_id):
	user = session.query(User).filter_by(id=user_id).one()
	return user

def getUserID (auth_id, auth_provider):
	try:
		user = session.query(User).filter_by(auth_id=auth_id, auth_site=auth_provider).one()
		return user.id
	except:
		return None