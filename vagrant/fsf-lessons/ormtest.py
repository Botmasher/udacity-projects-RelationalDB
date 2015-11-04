# CONFIG functions for manipulating python runtime
import sys

# CONFIG ORM
from sqlalchemy import Column, ForeignKey, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# CONFIG create foreign key relationships
from sqlalchemy.orm import relationship

# CONFIG use in creation code at end of file
from sqlalchemy import create_engine

# CONFIG make instance of imported declarative_base
# lets code know these correspond to tables in our db
Base = declarative_base()


# CLASS represent restaurants table, extending base class
class Restaurant (Base):
	# TABLE setup
	__tablename__ = 'restaurant'
	# MAPPER variables for columns in table
	name = Column (String(80), nullable = False)
	id = Column (Integer, primary_key = True)

# CLASS represent menu items table, extending base class	
class MenuItem (Base):
	# TABLE setup
	__tablename__ = 'menuitem'
	# MAPPER variables for columns in table
	name = Column (String(80), nullable = False)
	id = Column (Integer, primary_key = True)
	course = Column (String(250))
	price = Column (Float())
	description = Column (String(720))
	restaurant_id = Column (Integer, ForeignKey('restaurant.id'))
	# store relationship with my class restaurant
	restaurant = relationship (Restaurant)

## CONFIG end of file ##
# point to db - here create a sqlite file to sim db #
engine = create_engine('sqlite:///restaurantmenu.db')

# go into db, add classes created as new tables in db #
Base.metadata.create_all(engine)