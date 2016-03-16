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
	#flash("Messages work!")
	restaurants = session.query(Restaurant).all()
	o = '%s'%'Our ring of restaurants'
	o += '<ul>'
	for r in restaurants:
		o += '<li><a href="http://%s">%s</a> <a href="%s">(edit)</a></li>' % (r.website, r.name, url_for('restaurants_u',r_id=r.id))
	o += '</ul><p><a href="%s">+ new restaurant</a></p>'%(url_for('restaurants_c'))
	return render_template('main.php',content=o)

@app.route('/restaurants/create/', methods=['GET','POST'])
def restaurants_c():
	# get form template from WTForm class for this table
	form = RestaurantForm (request.form)

	# add restaurant to database
	if request.method == 'POST' and form.validate():
		new_row = Restaurant (name=form.name.data, address=form.address.data, city=form.city.data, state=form.state.data, zipCode=form.zipCode.data, website=form.website.data, cuisine=form.cuisine.data)
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
		flash ('This isn\'t the /edit/ you are looking for! We don\'t recognize that URL. Please try editing a /restaurant.')
		return redirect (url_for('home'))

	# edit database on form submission
	if request.method == 'POST' and form.validate():

		# make edits to the restaurant table
		if table == 'r_table':
			mod_row = session.query(Restaurant).filter_by(id=r_id)[0]
			mod_row.name = form.name.data
			mod_row.address = form.address.data
			mod_row.city = form.city.data
			mod_row.state = form.state.data
			mod_row.zipCode = form.zipCode.data
			mod_row.website = form.website.data
			mod_row.cuisine = form.cuisine.data
			flash ('This restaurant\'s profile has been updated!')

		# your edit URL has a variable for another table, like MenuItem
		# used for handling multiple tables at same url
		# e.g. /edit/<table_name>/<int:index>/
		elif table == 'otherTable':
			pass
		else:
			flash ('Unable to add your info to FoodBase. Don\'t leave yet! Please check that the form is completely filled out.')
			return redirect (url_for ('restaurants_u', r_id=r_id))

		# update row in the db
		session.add (mod_row)
		session.commit()

		return redirect (url_for('home'))

	# build the form here
	# 
	#
	# 
	return render_template('form.php', content='')

@app.route('/restaurants/<int:r_id>/delete/', methods=['GET','POST'])
def restaurants_d(r_id):
	o = '%s'%'Confirm - delete restaurant %s'%r_id
	return o

@app.route('/restaurants/<int:r_id>/menu/')
@app.route('/restaurants/<int:r_id>/')
def menu(r_id):
	o = '%s'%'List menu items for %s'%r_id
	return o

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