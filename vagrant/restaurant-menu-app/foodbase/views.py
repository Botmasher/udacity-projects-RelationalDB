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
	o = '<html><body>%s</body></html>'%'List restaurants. <ul><li><a href="/restaurants/0">rest0</a></li><li><a href="/restaurants/1">rest1</a></li></ul>'
	return o

@app.route('/restaurants/create/', methods=['GET','POST'])
def restaurants_c():
	o = '<html><body>%s</body></html>'%"Form - create a restaurant"
	return o

@app.route('/restaurants/edit/<int:r_id>/', methods=['GET','POST'])
def restaurants_u(r_id):
	o = '<html><body>%s</body></html>'%"Form - edit a restaurant"
	return o

@app.route('/restaurants/delete/<int:r_id>/', methods=['GET','POST'])
def restaurants_d(r_id):
	o = '<html><body>%s</body></html>'%"Confirm - delete a restaurant"
	return o

@app.route('/restaurants/<int:r_id>/menu/')
@app.route('/restaurants/<int:r_id>/')
def menu(r_id):
	o = '<html><body>%s</body></html>'%"List menu items"
	return o

@app.route('/restaurants/<int:r_id>/menu/create', methods=['GET','POST'])
def menu_c(r_id):
	o = '<html><body>%s</body></html>'%"Form - create a menu item for this restaurant."
	return o

@app.route('/restaurants/<int:r_id>/menu/edit/<int:m_id>/', methods=['GET','POST'])
def menu_u(r_id,m_id):
	o = '<html><body>%s</body></html>'%"Form - edit a menu item for this restaurant."
	return o

@app.route('/restaurants/<int:r_id>/menu/delete/<int:m_id>/', methods=['GET','POST'])
def menu_d(r_id,m_id):
	o = '<html><body>%s</body></html>'%"Confirm - delete a menu item from this restaurant."
	return o