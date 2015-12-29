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

# CLASS represent restaurants table, extending base class
class Restaurant (Base):
	# TABLE setup
	__tablename__ = 'restaurant'

	# MAPPER variables for columns in table
	name = Column(String(80), nullable = False)
	address = Column(String(250), nullable = False)
	city = Column(String(250), nullable = False)
	zipCode = Column(Integer)
	state = Column(String(250), nullable = False)
	website = Column(String(250), nullable = False)
	id = Column(Integer, primary_key = True)

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
	restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
	# store relationship with key table
	restaurant = relationship(Restaurant)

# ## CONFIG end of file ##
# # point to db - here create a sqlite file to sim db #
# engine = create_engine('sqlite:///foodbase/models.db')

# # go into db, add classes created as new tables in db #
# Base.metadata.create_all(engine)

# # CRUD session
# Base.metadata.bind = engine
# DBSession = sessionmaker (bind = engine)	# possibility to CRUD
# session = DBSession()	# open instance of the DBSession