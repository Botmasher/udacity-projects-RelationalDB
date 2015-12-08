from flask import Flask
from flask_testing import TestCase
import unittest

from fluppybase import create_app, db

class MyTest(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite://test.db"
    TESTING = True

    def create_app(self):
        return create_app(self)

    def setUp(self):
        db.create_all()

    def dbTest(self):
    	puppy = Puppy()
    	db.session.add(puppy)
    	db.session.commit()

    	assert puppy in db.session
    	response = self.client.get("/")
    	assert puppy in db.session

    def tearDown(self):
        db.session.remove()
        db.drop_all()

if __name__ == '__main__':
	unittest.main()