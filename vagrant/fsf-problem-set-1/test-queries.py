import datetime
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
#from sqlalchemy import select

# our database, as described in the section above
from puppies_db_setup import Base, Puppy, Shelter, Profile
engine = create_engine('sqlite:///puppies.db')
Base.metadata.bind = engine

# CRUD requires a session
DBSession = sessionmaker (bind = engine)	# possibility to CRUD
session = DBSession()	# open instance of the DBSession

# Query all puppy results in ascending alphabetical order
puppies = session.query(Puppy).order_by(asc('puppy.name')).all()
print ('\n\nLINE THEM UP FOR FORMULAIC INTRODUCTION\n')
for p in puppies:
	print ('Greetings! I am %s, and I am a shelter puppy!'%p.name)

# Query all of the puppies that are less than 6 months old organized by youngest first
sixMonthsAgo = datetime.datetime.utcnow() - datetime.timedelta(weeks=25)
puppies = session.query(Puppy, Profile).filter(Profile.dateOfBirth > sixMonthsAgo).order_by((asc('profile.dateOfBirth')))
print ('\n\nBEGIN ACCEPTABLE LIST - PUPPIES LESS THAN SIX MONTHS OLD\n')
for p in puppies:
	print ('Hi. %s here, all young and peppy. I was born %s.'%(p[0].name, p[1].dateOfBirth))

# Query all puppies by ascending weight
puppies = session.query(Puppy, Profile).order_by(asc('profile.weight')).all()
print ('\n\nPASS FLUBBER JUDGMENT - THINNEST TO CHUNKIEST\n')
for p in puppies:
	print ('Hi again. I hope I am not a fat puppy. My name is %s. I weigh %s.'%(p[0].name,p[1].weight))

# Query all puppies grouped by their shelter
puppies = session.query(Puppy).order_by('puppy.shelter_id').group_by('puppy.name').all()
print ('\n\nIDENTIFY KILL LOCATIONS - CURRENT HOLDING CELLS\n')
for p in puppies:
	p.shelter.set_occupancy(p.shelter_id, 2)
	p.shelter.set_capacity(p.shelter_id, 100)
	print ('Hi, just one more time. I am a homeless puppy. My name is %s. Right now I live at %s. %s / %s'%(p.name,p.shelter.name,p.shelter.occupancy,p.shelter.capacity))