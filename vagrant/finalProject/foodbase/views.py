from foodbase import app

from flask import render_template, request, redirect, url_for, flash, jsonify

import math

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
	flash("Messages work!")
	o = '<html><body>%s</body></html>'%'List restaurants'
	return render_template('main.php',content=o)

@app.route('/restaurants/create/', methods=['GET','POST'])
def restaurants_c():
	o = '<html><body>%s</body></html>'%'Form - create a restaurant'
	return o

@app.route('/restaurants/<int:r_id>/edit/', methods=['GET','POST'])
def restaurants_u(r_id):
	o = '<html><body>%s</body></html>'%'Form - edit restaurant %s'%r_id
	return o

@app.route('/restaurants/<int:r_id>/delete/', methods=['GET','POST'])
def restaurants_d(r_id):
	o = '<html><body>%s</body></html>'%'Confirm - delete restaurant %s'%r_id
	return o

@app.route('/restaurants/<int:r_id>/menu/')
@app.route('/restaurants/<int:r_id>/')
def menu(r_id):
	o = '<html><body>%s</body></html>'%'List menu items for %s'%r_id
	return o

@app.route('/restaurants/<int:r_id>/menu/create', methods=['GET','POST'])
def menu_c(r_id):
	o = '<html><body>%s</body></html>'%'Form - create a menu item for %s'%r_id
	return o

@app.route('/restaurants/<int:r_id>/menu/<int:m_id>/edit/', methods=['GET','POST'])
def menu_u(r_id,m_id):
	o = '<html><body>%s</body></html>'%'Form - edit menu item %s for %s'%(m_id,r_id)
	return o

@app.route('/restaurants/<int:r_id>/menu/<int:m_id>/delete/', methods=['GET','POST'])
def menu_d(r_id,m_id):
	o = '<html><body>%s</body></html>'%'Confirm - delete menu item %s from restaurant %s'%(m_id,r_id)
	return o