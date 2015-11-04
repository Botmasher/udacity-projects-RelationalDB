# basic flask stuff
from flask import Flask
app = Flask (__name__)

# sqlalchemy stuff
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# setup connection for restaurant db
from ormtest import Base,Restaurant,MenuItem
engine = create_engine ('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# mock up a little test database with my orm classes
menu_items = ['this pizza', 'that pizza', 'thother pizza', 'nuffies pizza']
menu_prices = [9.50, 8.99, 10.95, 7.00]
menu_desc = ['No man can has cheesier than this one. And that is the Germanic people manniz, meaning everyone.','That sauce is better with more sauce.', 'Finally... a pizza that takes being a pizza seriously.', 'You can\'t eat the void but you can pay for it.']
session.query(MenuItem).delete()
# refill tables
for x in range(0,len(menu_items)):
	new_item = MenuItem (name=menu_items[x], price=menu_prices[x], description=menu_desc[x], restaurant_id=1)
	session.add(new_item)
session.commit()					# persist the changes

# decorator functions to catch routes
@app.route('/')
@app.route('/hello')
# if successfully route, execute this
def HelloWorld ():
	restaurant = session.query(Restaurant).first()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
	output = ''
	for i in items:
		output += '<h2>'+i.name+'</h2>'
		output += '<p>'+'{0:.2f}'.format(round(i.price,2))+'</p>'
		output += '<p>'+i.description+'</p>'
	return output

# run if this is app but not if imported as module
if __name__ == '__main__':
	# reload server every time notice code change
	app.debug = True
	# for accessing and running on vagrant
	app.run(host = '0.0.0.0', port = 5000)