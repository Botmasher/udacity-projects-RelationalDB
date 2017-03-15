# CONFIG functions for manipulating python runtime
import sys

# CONFIG ORM
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Date, Numeric

from sqlalchemy.ext.declarative import declarative_base

# add sql update methods
from sqlalchemy import update

# functions (count, etc.)
from sqlalchemy import func

# CONFIG create foreign key relationships and allow opening sessions
from sqlalchemy.orm import relationship, sessionmaker

# CONFIG use in creation code at end of file
from sqlalchemy import create_engine

# CONFIG setup base class
Base = declarative_base()

# set to True for models_reset() - wipe db
reset = False

# User class added for oauth2 / local permissions
class User (Base):
	__tablename__ = 'user'
	id = Column(Integer, primary_key = True)
	name = Column(String(250), nullable = False)
	auth_id = Column(String(800, nullable = False)
	auth_site = Column(String(80), nullable = False)
	picture = Column(String(800))
	email = Column(String(800), nullable = True)
	city = Column(String(100), nullable = True)
	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'auth_id': self.auth_id,
			'auth_site': self.auth_site,
			'picture': self.picture,
			'email': self.email,
			'city': self.city
		}

# CLASS represent restaurants table, extending base class
class Restaurant (Base):
	# TABLE setup
	__tablename__ = 'restaurant'

	# MAPPER variables for columns in table
	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	address = Column(String(250), nullable = False)
	city = Column(String(100), nullable = False)
	zipCode = Column(Integer, nullable = True)
	state = Column(String(80), nullable = True)
	cuisine = Column(String(100), nullable = True)
	website = Column(String(250), nullable = True)
	image = Column(String(250), nullable = True)
	children = relationship('MenuItem')
	# store relationship with user table
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	# serialize JSON data for API
	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'address': self.address,
			'city': self.city,
			'zipCode': self.zipCode,
			'state': self.state,
			'website': self.website,
			'cuisine': self.cuisine,
			'image': self.image,
			'user': self.user
		}

# CLASS represent menu items table, extending base class	
class MenuItem (Base):
	# TABLE setup
	__tablename__ = 'menu_item'

	# MAPPER variables for columns in table
	id = Column(Integer, primary_key = True)
	name = Column(String(250), nullable = False)
	description = Column(String(800), nullable = False)
	# store relationship with key table
	restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
	restaurant = relationship(Restaurant)
	# store relationship with user table
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	# serialize JSON data for API
	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'description': self.description,
			'restaurant': self.restaurant,
			'user': self.user
		}

## CONFIG end of file ##
# point to db - here create a sqlite file to sim db #
#engine = create_engine('sqlite:///foodbase/models.db')
engine = create_engine('sqlite:///modelswithusers.db')

# go into db, add classes created as new tables in db #
Base.metadata.create_all(engine)

# CRUD session
Base.metadata.bind = engine
DBSession = sessionmaker (bind = engine)	# possibility to CRUD
session = DBSession()	# open instance of the DBSession

# /!\ Wipe and refresh the db
def models_reset():
	session.query(Restaurant).delete()
	session.query(MenuItem).delete()
	r1 = Restaurant(name='Pizzastro',address='123 Lucky St',city='Pizzopolis',zipCode='11111',state='KY',website='www.pizzamenowclown.com',cuisine='Pizzation')
	session.add(r1)
	session.commit()
	for res in session.query(Restaurant):
		print res.name
	return None

# /!\ Runs the db reset above
if (reset == True):
	models_reset()