from foodbase import app

from flask import render_template, request, redirect, url_for, flash, jsonify

import math

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

@app.route('/restaurants/')
def restaurants():
	restaurants = session.query(Restaurant).all()
	o = '%s'%'Our ring of restaurants'
	o += '<ul>'
	for r in restaurants:
		o += '<li><a href="%s">%s</a> <a href="%s">(edit)</a> <a href="%s">(delete)</a></li>' % (url_for('menu', r_id=r.id), r.name, url_for('restaurants_u',r_id=r.id), url_for('restaurants_d',r_id=r.id))
	o += '</ul><p><a href="%s">+ new restaurant</a></p>'%(url_for('add', table='Restaurant'))
	return render_template('main.php',content=o)

@app.route('/restaurants/<int:r_id>/menu/')
@app.route('/restaurants/<int:r_id>/')
def menu(r_id):
	r = session.query(Restaurant).filter_by(id=r_id)[0]
	m = session.query(MenuItem).filter_by(restaurant_id=r_id)
	o = '<p>%s - main menu</p>'%r.name
	o += '<ul>'
	for i in m:
		o += '<li>%s<br>%s<br>%s %s</li>'%(m.name,m.description,'edit url', 'delete url') 
	o += '</ul>'
	o += '<p><a href="%s">+ new item</a></p>' % (url_for('add',table='MenuItem'))
	return render_template ('main.php',content=o)

@app.route('/add/<table>/', methods=['GET','POST'])
def add (table):
	# get form template from WTForm class for this table
	form = RestaurantForm (request.form)
	if table == 'Restaurant':
		form = RestaurantForm(request.form)
	elif table == 'MenuItem':
		form = MenuItemForm(request.form)
	else:
		flash ('I didn\'t understand! Please try adding a /Restaurant/ or a /MenuItem/.')
	# add restaurant to database
	if request.method == 'POST' and form.validate():
		if table == 'Restaurant':
			new_row = Restaurant (name=form.name.data, address=form.address.data, city=form.city.data, state=form.state.data, zipCode=form.zipCode.data, website=form.website.data, cuisine=form.cuisine.data)
		elif table == 'MenuItem':
			new_row = MenuItem (name=form.name.data, description=form.description.data, restaurant_id=form.restaurant_id.data)
		else:
			flash ('')
		session.add (new_row)
		session.commit ()
		return redirect (url_for('home'))
		
	# display form for adding restaurant
	return render_template ('form.php', form=form, content='')

@app.route('/restaurants/<int:r_id>/edit/', methods=['GET','POST'])
def restaurants_u(r_id):
	# retrieve form class from forms.py based on URL keyword
	table = 'r_table'
	if table == 'r_table':
		form = RestaurantForm (request.form)
	else:
		flash ('This isn\'t the /edit/ you are looking for! We don\'t recognize that URL.')
		return redirect (url_for('home'))

	# POST - edit database on form submission
	if request.method == 'POST' and form.validate():

		# make edits to the restaurant table
		if table == 'r_table':
			mod_row = session.query(Restaurant).filter_by(id=r_id)[0]
			mod_row.name = form.name.data
			mod_row.cuisine = form.cuisine.data
			mod_row.address = form.address.data
			mod_row.city = form.city.data
			mod_row.state = form.state.data
			mod_row.zipCode = form.zipCode.data
			mod_row.website = form.website.data
			flash ('I updated the profile for %s!'%mod_row.name)

		# your edit URL has a variable for another table, like MenuItem
		# build out to use for handling multiple tables at same url
		# e.g. /edit/<table_name>/<int:index>/
		elif table == 'otherTable':
			pass
		else:
			flash ('Help, I couldn\'t add that info to FoodBase! Do you mind checking if you filled out the whole form?')
			return redirect (url_for('restaurants_u', r_id=r_id))

		# update row in the db
		session.add (mod_row)
		session.commit()

		return redirect (url_for('home'))

	# GET - retreive form data and build the form
	if table == 'r_table':
		# if user requests update restaurant form
		r = session.query(Restaurant).filter_by(id=r_id)[0]
		form.name.data = r.name
		form.cuisine.data = r.cuisine
		form.address.data = r.address
		form.city.data = r.city
		form.state.data = r.state
		form.zipCode.data = r.zipCode
		form.website.data = r.website
	else:
		# if user requests other update forms
		pass
	return render_template('form.php', form=form, content='')

@app.route('/restaurants/<int:r_id>/delete/', methods=['GET','POST'])
def restaurants_d(r_id):
	# retrieve form class from forms.py based on URL keyword
	table = 'r_table'

	# make edits to the restaurant table
	if table == 'r_table':
		mod_row = session.query(Restaurant).filter_by(id=r_id)[0]

	# your URL has a variable for another table, like MenuItem
	# build out to handle multiple tables at same route
	# e.g. /edit/<table_name>/<int:index>/
	elif table == 'otherTable':
		# mod_row = session.query(OtherTable).filter_by(id=other_id)[0]
		pass
	else:
		flash ('I couldn\'t delete that info from FoodBase!')
		return redirect (url_for('home'))

	# POST - edit database on form submission
	if request.method == 'POST':
		
		# delete selected row
		session.delete (mod_row)
		session.commit()

		flash ('I erased that information from FoodBase!')

		return redirect (url_for('home'))

	# GET - retreive form data and build the form
	o = '<p>Do you really want to delete %s?</p>\
		<form action="" method="POST"><button>Remove it!</button></form> \
		<a href="%s">NO! Go home!</a>'%(mod_row.name, url_for('home'))
	return render_template('main.php', content=o)

@app.route('/restaurants/<int:r_id>/menu/create', methods=['GET','POST'])
def menu_c(r_id):
	o = '%s'%'Form - create a menu item for %s'%r_id
	return o

@app.route('/restaurants/<int:r_id>/menu/<int:m_id>/edit/', methods=['GET','POST'])
def menu_u(r_id,m_id):
	o = '%s'%'Form - edit menu item %s for %s'%(m_id,r_id)
	return o

@app.route('/restaurants/<int:r_id>/menu/<int:m_id>/delete/', methods=['GET','POST'])
def menu_d(r_id,m_id):
	o = '%s'%'Confirm - delete menu item %s from restaurant %s'%(m_id,r_id)
	return o