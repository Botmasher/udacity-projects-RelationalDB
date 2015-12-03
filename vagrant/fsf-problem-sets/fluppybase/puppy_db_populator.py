from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from puppies_db_setup import Base, Shelter, Puppy, Profile, Adopter, curate_shelter_capacity
#from flask.ext.sqlalchemy import SQLAlchemy
from random import randint
import datetime
import random


engine = create_engine('sqlite:///fluppybase/puppies.db')

Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)

session = DBSession()


# wipe the db
def DB_Wipe ():
    session.query(Adopter).delete()
    session.query(Profile).delete()
    session.query(Puppy).delete()
    session.query(Shelter).delete()
    session.commit()

#Add Shelters
def Add_Shelters ():
    shelter1 = Shelter(name = "Oakland Animal Services", address = "1101 29th Ave", city = "Oakland", state = "California", zipCode = "94601", website = "oaklandanimalservices.org", capacity = 52)
    session.add(shelter1)

    shelter2 = Shelter(name = "San Francisco SPCA Mission Adoption Center", address="250 Florida St", city="San Francisco", state="California", zipCode = "94103", website = "sfspca.org", capacity = 33)
    session.add(shelter2)

    shelter3 = Shelter(name = "Wonder Dog Rescue", address= "2926 16th Street", city = "San Francisco", state = "California" , zipCode = "94103", website = "http://wonderdogrescue.org", capacity = 27)
    session.add(shelter3)

    shelter4 = Shelter(name = "Humane Society of Alameda", address = "PO Box 1571" ,city = "Alameda" ,state = "California", zipCode = "94501", website = "hsalameda.org", capacity = 30)
    session.add(shelter4)

    shelter5 = Shelter(name = "Palo Alto Humane Society" ,address = "1149 Chestnut St." ,city = "Menlo Park", state = "California" ,zipCode = "94025", website = "paloaltohumane.org", capacity = 45)
    session.add(shelter5)

#This method will make a random age for each puppy between 0-18 months(approx.) old from the day the algorithm was run.
def CreateRandomAge():
    today = datetime.date.today()
    days_old = randint(0,540)
    birthday = today - datetime.timedelta(days = days_old)
    return birthday

#This method will create a random weight between 1.0-40.0 pounds (or whatever unit of measure you prefer)
def CreateRandomWeight():
    return random.uniform(1.0, 40.0)

#Add Puppies abd
def Add_Puppies ():
    male_names = ["Bailey", "Max", "Charlie", "Buddy","Rocky","Jake", "Jack", "Toby", "Cody", "Buster", "Duke", "Cooper", "Riley", "Harley", "Bear", "Tucker", "Murphy", "Lucky", "Oliver", "Sam", "Oscar", "Teddy", "Winston", "Sammy", "Rusty", "Shadow", "Gizmo", "Bentley", "Zeus", "Jackson", "Baxter", "Bandit", "Gus", "Samson", "Milo", "Rudy", "Louie", "Hunter", "Casey", "Rocco", "Sparky", "Joey", "Bruno", "Beau", "Dakota", "Maximus", "Romeo", "Boomer", "Luke", "Henry"]

    female_names = ['Bella', 'Lucy', 'Molly', 'Daisy', 'Maggie', 'Sophie', 'Sadie', 'Chloe', 'Bailey', 'Lola', 'Zoe', 'Abby', 'Ginger', 'Roxy', 'Gracie', 'Coco', 'Sasha', 'Lily', 'Angel', 'Princess','Emma', 'Annie', 'Rosie', 'Ruby', 'Lady', 'Missy', 'Lilly', 'Mia', 'Katie', 'Zoey', 'Madison', 'Stella', 'Penny', 'Belle', 'Casey', 'Samantha', 'Holly', 'Lexi', 'Lulu', 'Brandy', 'Jasmine', 'Shelby', 'Sandy', 'Roxie', 'Pepper', 'Heidi', 'Luna', 'Dixie', 'Honey', 'Dakota']

    puppy_images = ["http://mrg.bz/cVAmXh", "http://mrg.bz/Es7wC9","http://mrg.bz/MzcQxz","http://mrg.bz/Y6YpBK","http://mrg.bz/JMvg3T","http://mrg.bz/goO8gI","http://mrg.bz/mjirHQ","http://mrg.bz/WsosUg","http://mrg.bz/WDFvjp","http://mrg.bz/vfYJXo","http://mrg.bz/vfYJXo","http://mrg.bz/cTsN3l"]

    for i,x in enumerate(male_names):
        new_puppy = Puppy(name = x, shelter_id=randint(1,5))
        new_profile = Profile(gender = "male", dateOfBirth = CreateRandomAge(),picture=random.choice(puppy_images), weight = CreateRandomWeight(), puppy_id = new_puppy.id)
        session.add(new_puppy)
        session.add(new_profile)
        session.commit()

    for i,x in enumerate(female_names):
        new_puppy = Puppy(name = x, shelter_id=randint(1,5))
        new_profile = Profile(gender = "female", dateOfBirth=CreateRandomAge(),picture=random.choice(puppy_images), weight = CreateRandomWeight(), puppy_id = new_puppy.id)
        session.add(new_puppy)
        session.add(new_profile)
        session.commit()


# reset and recreate the DB
def Create_DB ():
    
    DB_Wipe()
    Add_Shelters()
    Add_Puppies()
    
    # fill in occupancy for each shelter by counting puppies (capacity already set above)
    curate_shelter_capacity()