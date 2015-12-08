#!flask/bin/python
import os
import unittest

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from fluppybase import app, db
from fluppybase.puppies_db_setup import Base, Puppy, Adopter, Shelter, Profile
import fluppybase.puppy_db_populator

# CONFIG setup base class
Base = declarative_base()
engine = create_engine('sqlite:///test.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
Base.metadata.create_all(engine)
TESTING = True

class TestCase(unittest.TestCase):

    def setUp(self):

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()

        #fluppybase.puppy_db_populator.Create_DB()

        # proper way to build up - currently broken because no db=SQLalchemy(app)
        db.create_all()

    def tearDown(self):
        return None
        # proper way to tear down - currently not working because no SQLAlchemy(app) to import
        db.session.remove()
        db.drop_all()

    def test_not_empty_db (self):
        rv = self.app.get('/')
        assert 'No entries here so far' not in rv.data

    def test_add_puppy_ (self):
        #rv = self.app.get('/add/puppy/', data=dict(name=''))
        puppy = Puppy(name='Amigo2')
        session.add(puppy)
        session.commit()
        assert puppy.name == 'Amigo2'

if __name__ == '__main__':
    unittest.main()