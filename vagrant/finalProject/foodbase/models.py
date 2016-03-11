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

# run models_reset at bottom of file
reset = False

# CLASS represent restaurants table, extending base class
class Restaurant (Base):
	# TABLE setup
	__tablename__ = 'restaurant'

	# MAPPER variables for columns in table
	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	address = Column(String(250), nullable = False)
	city = Column(String(100), nullable = False)
	zipCode = Column(Integer, nullable = False)
	state = Column(String(80), nullable = False)
	cuisine = Column(String(100), nullable = False)
	website = Column(String(250), nullable = False)
	children = relationship('MenuItem')

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
			'website': self.website
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

	# serialize JSON data for API
	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'description': self.description,
			'restaurant': self.restaurant
		}

## CONFIG end of file ##
# point to db - here create a sqlite file to sim db #
engine = create_engine('sqlite:///models.db')

# go into db, add classes created as new tables in db #
Base.metadata.create_all(engine)

# CRUD session
Base.metadata.bind = engine
DBSession = sessionmaker (bind = engine)	# possibility to CRUD
session = DBSession()	# open instance of the DBSession

def models_reset():
	session.query(Restaurant).delete()
	session.query(MenuItem).delete()
	r1 = Restaurant(name='Pizzastro',address='123 Lucky St',city='Pizzopolis',zipCode='11111',state='KY',website='www.pizzamenowclown.com',cuisine='Pizzation')
	session.add(r1)
	session.commit()
	for res in session.query(Restaurant):
		print res.name
	return None

if (reset == True):
	models_reset()