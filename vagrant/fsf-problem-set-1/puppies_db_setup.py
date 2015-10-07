# CONFIG functions for manipulating python runtime
import sys

# CONFIG ORM
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base

# CONFIG create foreign key relationships
from sqlalchemy.orm import relationship

# CONFIG use in creation code at end of file
from sqlalchemy import create_engine

# CONFIG setup base class
Base = declarative_base()

# CLASS represent restaurants table, extending base class
class Shelter (Base):
	# TABLE setup
	__tablename__ = 'shelter'
	# MAPPER variables for columns in table
	name = Column(String(80), nullable = False)
	address = Column(String(250), nullable = False)
	city = Column(String(250), nullable = False)
	zipCode = Column(Integer)
	state = Column(String(250), nullable = False)
	website = Column(String(250), nullable = False)
	id = Column(Integer, primary_key = True)

# CLASS represent menu items table, extending base class	
class Puppy (Base):
	# TABLE setup
	__tablename__ = 'puppy'
	# MAPPER variables for columns in table
	id = Column(Integer, primary_key = True)
	name = Column(String(250), nullable = False)
	breed = Column(String(80))
	gender = Column(String(80), nullable = False)
	dateOfBirth = Column(Date)
	picture = Column(String)
	shelter_id = Column(Integer, ForeignKey('shelter.id'))
	# store relationship with foreign key table
	shelter = relationship(Shelter)
	weight = Column(Integer)

## CONFIG end of file ##
# point to db - here create a sqlite file to sim db #
engine = create_engine('sqlite:///puppies.db')

# go into db, add classes created as new tables in db #
Base.metadata.create_all(engine)