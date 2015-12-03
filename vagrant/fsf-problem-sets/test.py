from flask_testing import TestCase
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fluppybase.puppies_db_setup import Base, Shelter, Puppy, Profile, Adopter, curate_shelter_capacity
from fluppybase import app, puppies_db_setup, puppy_db_populator

class MyTest(TestCase):

	engine = create_engine('sqlite:///test.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	TESTING = True

	def create_app(self):
		return create_app(self)

	def setUp(self):
		puppies_db_setup.create_all()
		#puppy_db_populator.Create_All()
		print (session.query(Puppy).first()[0])

	def tearDown (self):
		session.remove()
		puppies_db_setup.drop_all()

if __name__ == '__main__':
	unittest.main()