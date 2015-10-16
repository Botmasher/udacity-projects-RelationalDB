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
	occupancy = Column(Integer)
	capacity = Column(Integer)
	id = Column(Integer, primary_key = True)

# ASSOCIATION table for many:many between puppies and adopters
association_table = Table('association', Base.metadata, Column('left_id', Integer, ForeignKey('puppy.id')), Column('right_id', Integer, ForeignKey('adopter.id')))

# CLASS represent menu items table, extending base class	
class Puppy (Base):
	# TABLE setup
	__tablename__ = 'puppy'
	# MAPPER variables for columns in table
	id = Column(Integer, primary_key = True)
	name = Column(String(250), nullable = False)
	shelter_id = Column(Integer, ForeignKey('shelter.id'))
	# store relationship with key table
	shelter = relationship(Shelter)
	# ASSOCIATION store one-to-one relationship with child table
	profile = relationship('Profile', uselist=False, backref='puppy')
	# ASSOCIATION store many-to-many relationship with child table
	adopter = relationship('Adopter', secondary=association_table, backref='puppy')

# added relation for puppy adopter - many:many association to puppy
class Adopter (Base):
	__tablename__ = 'adopter'
	id = Column(Integer, primary_key = True)
	name = Column(String(250))

# added relation for puppy profile - 1:1 association to puppy
class Profile (Base):
	__tablename__ = 'profile'
	id = Column(Integer, primary_key = True)
	breed = Column(String(80))
	gender = Column(String(80), nullable = False)
	weight = Column(Integer)
	dateOfBirth = Column(Date)
	picture = Column(String)
	# store relationship with foreign key table
	puppy_id = Column(Integer, ForeignKey('puppy.id'))

## CONFIG end of file ##
# point to db - here create a sqlite file to sim db #
engine = create_engine('sqlite:///puppies.db')

# go into db, add classes created as new tables in db #
Base.metadata.create_all(engine)

# CRUD session
Base.metadata.bind = engine
DBSession = sessionmaker (bind = engine)	# possibility to CRUD
session = DBSession()	# open instance of the DBSession


# get and set shelter current and max occupancy
def get_occupancy (shelter_id):
	result = session.query (Shelter).filter(Shelter.id==shelter_id).all()
	return result
def set_occupancy (shelter_id, occupancy):
	result = session.execute ( update(Shelter).where(Shelter.id==shelter_id)\
		.values (occupancy=occupancy) )
	return result
def set_capacity (shelter_id, capacity):
	result = session.execute ( update(Shelter).where(Shelter.id==shelter_id)\
		.values (capacity=capacity) )
	return result

# check a puppy into a shelter
def check_in (puppy_id, shelter_id):
	# query for requested shelter table
	row = session.query(Shelter).filter(Shelter.id==shelter_id).one()
	# if requested shelter is full, iterate through to find an open one
	if row.occupancy >= row.capacity:
		print ("Shelter full. Checking for another shelter...\n")
		table = session.query(Shelter).all()
		for r in table:
			# if newly chosen shelter is open, check puppy in
			if r.occupancy < r.capacity:
				shelter_id = r.id
				result = session.execute ( update(Puppy).where(Puppy.id == puppy_id).values (shelter_id=shelter_id) )
				print ("Found a new shelter! Checking puppy into %s."%(r.name))
				return result
			# keep checking for open shelter
			else:
				pass
		# if iteration returned no shelter, all shelters are full
		print ("All shelters are full. Please open a new one.")
		return None
	# requested shelter isn't full, so check puppy in
	else:
		result = session.execute ( update(Puppy).where(Puppy.id == puppy_id).values (shelter_id=shelter_id) )
		print ("As requested, checking puppy into %s."%(row.name))
		return result


def curate_shelter_capacity (reset_cap=False):
	"""Update the occupancy and capacity of each shelter to reflect current totals.

	:param reset_cap: Boolean option to reset the capacity of each shelter
	:returns: None
	"""
	# reset shelter capacity if requested
	this_cap = Shelter.capacity if not reset_cap else 30
	
	# sum the puppies in each shelter
	shelters = session.query(Puppy.shelter_id, func.count(Puppy.id)).group_by(Puppy.shelter_id).all()
	# update each shelter with its current number of puppies
	for shelter in shelters:
		session.execute ( update(Shelter).where(Shelter.id == shelter[0]).values (occupancy=shelter[1], capacity=this_cap) )
	return None


# write a load-balancing algorithm that evenly distributes puppies throughout all shelters

# query for the number of puppies
# query for the sum of occupancies
# query for the sum of capacities
# ratio the two

# redistribute puppies evenly
	# for each shelter, while shelter ratio is less than that overall ratio,
	# put puppies in it
	#	- use manual counter starts at 0/Shelter.capacity
	#	- go down Puppy.id and place puppies, increase counter
	#	- prompt to open more shelters if reach cap

# if we end up with extra puppies (number of puppies still counting thru)
	# - figure out how many left
	# - divide between number of shelters if still under cap
	# - prompt to open more once reach cap


def distribute_puppies ():
	# calculate totals to determine overall balance 
	total_puppies_to_place = session.query(func.count(Puppy.id)).first()[0]
	total_occupancy = float( session.query(func.sum(Shelter.occupancy)).first()[0] )
	total_capacity = float( session.query(func.sum(Shelter.capacity)).first()[0] )
	total_ratio = total_occupancy/total_capacity
 
 	# balance individual shelters to overall balance
	for shelter in session.query(Shelter.id, Shelter.capacity).all():
		# count values for determining when shelter is balanced
		shelter_counter = 0
		shelter_balance = total_ratio * shelter[1]
		while shelter_counter < shelter_balance:
			# count down puppies and add them to shelter, highest to lowest id
			session.execute(update(Puppy).where(Puppy.id == total_puppies_to_place).values(shelter_id=shelter[0]))
			# increment/decrement balance values
			total_puppies_to_place -= 1
			shelter_counter += 1


	# balance any remaining puppies
	this_shelter = 0
	while total_puppies_to_place > 0:
		# if all shelters are full, prompt user to open a new shelter
		if session.query(func.sum(Shelter.occupancy)).first()[0] >= session.query(func.sum(Shelter.capacity)).first()[0]:
			print ('We placed as many puppies as possible, but there aren\'t enough shelters! Please consider opening a new one!')
			return None
		else:
			# place this puppy
			session.execute(update(Puppy).where(Puppy.id==total_puppies_to_place).values(shelter_id=this_shelter))
			
			# countdown puppy id for next pass through loop
			total_puppies_to_place -= 1
			
			# determine shelter id for next pass through loop
			if  this_shelter >= session.query(func.count(Shelter.id)).first()[0]:
				this_shelter = 0
			else:
				this_shelter += 1


	# EXTRA challenge (by Josh): move puppies as little as possible!
	return None


# test adding occupancy and capacity to a shelter
#print(str(get_occupancy(1).occupancy)+'/'+str(get_occupancy(1).capacity))

# test checking in puppy
#check_in(1,1)

# test for shelter counts
for x in session.query (Shelter.name, Shelter.occupancy, Shelter.capacity).all():
	print (str(x[0]) + ': ' + str(x[1]) + ' / '+ str(x[2]))

# run occupancy functions
curate_shelter_capacity()
set_capacity(1,32)
set_capacity(3,26)
set_capacity(4,40)
distribute_puppies()
curate_shelter_capacity()

# save changes
session.commit()

# test for shelter counts
for x in session.query (Shelter.name, Shelter.occupancy, Shelter.capacity).all():
	print (str(x[0]) + ': ' + str(x[1]) + ' / '+ str(x[2]))

# test for puppies in shelters
#for x in session.query (Puppy.name, Shelter.name, Shelter.occupancy, Shelter.capacity).filter(Puppy.shelter_id==Shelter.id).all():
#	print (str(x[0]) + ': ' + str(x[1]) + ' -- ' + str(x[2]) + ' / '+ str(x[3]))