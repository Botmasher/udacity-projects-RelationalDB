# app in subfolder following Simple Package structure
# http://flask.pocoo.org/docs/0.10/patterns/packages/#simple-packages
from fluppybase import app

if __name__ == '__main__':
	# reload server every time notice code change
	app.debug = False
	# session secret key for message flashing
	app.secret_key = 'super_secret_key'

	# error logging
	if not app.debug:
		import logging
		logging.basicConfig (filename='debug.log', level=logging.DEBUG)
	
	# for accessing and running on vagrant
	app.run(host = '0.0.0.0', port = 5000)