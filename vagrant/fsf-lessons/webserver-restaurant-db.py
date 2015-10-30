from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# decipher messages sent by server
import cgi

# sql and orm
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

# import restaurant db classes
from ormtest import Restaurant,MenuItem
engine = create_engine('sqlite:///restaurantmenu.db')

# start a session for CRUD actions
Base.metadata.bind = engine
DBSession = sessionmaker (bind = engine)
session = DBSession()

# mock up a little test database with my orm classes
new_restaurants = ['John\'s House', 'Pizza Nut', 'Spanish Salsa', 'Gobbledies', 'Beganensis'] 
session.query(Restaurant).delete()	# clear out all entries from both tables
session.query(MenuItem).delete()	# clear out all entries from both tables
# refill tables
for n in new_restaurants:
	new_restaurant = Restaurant(name=n)
	session.add(new_restaurant)
session.commit()					# persist the changes


# this is our handler that gets used when server is started in main()
class webserverHandler (BaseHTTPRequestHandler):
	# do_GET request handles all GET requests the server receives
	def do_GET(self):
		try:
			# check path (url sent by server as string)
			if self.path.endswith('/restaurants'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()	# blank line indicating end of headers
			
				# list all restaurants (see db and orm imports at top of this file)
				restaurants = session.query(Restaurant).order_by(asc('restaurant.name')).all()
				output = ''
				output += '<html><body>'
				for r in restaurants:
					output += '<h2> %s </h2>'%r.name
					output += '<form method="POST" enctype="multipart/form-data" action="/restaurants"><input name="new_restaurant" type="text"><input type="submit" value="Submit"></form>'
				output += '</body></html>'
				# send an output stream message back to the client
				self.wfile.write(output)
				return

			# do a separate branch for a different URL
			elif self.path.endswith('/hola'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ''
				output += '<html><body>&#161;Hola!'
				output += '<h2> Leave a message at the beep! </h2>'

				output += '<form method = \'POST\' enctype=\'multipart/form-data\' action=\'/hello\'><h2>beeeeeeeep . . . ...</h2><input name = \'message\' type=\'text\'><input type=\'submit\' value=\'Submit\'></form>'
				output += '</body></html>'
				self.wfile.write(output)
				return
		
		# what to do if file not found
		except:
			self.send_error(404, 'File not found %s'%self.path)

	def do_POST (self):
		try:
			# this is the post response
			self.send_response(301)
			self.end_headers()

			# store the header's main value and dictionary of parameters
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			# if the content is form data, collect all its fields with parse_multipart
			if ctype == 'multipart/form-data':
				fields = cgi.parse_multipart(self.rfile, pdict)
				# store specific fields into array (here the ones named 'message')
				messagecontent = fields.get('message')

			# now tell client what to do with info received
			output = ''
			output += '<html><body>'
			output += '<h2> Leave a message at the beep! </h2>'
			output += '<h1>%s</h1>'%messagecontent[0]

			output += '<form method = \'POST\' enctype=\'multipart/form-data\' action=\'/hello\'><h2>beeeeeeeep . . . ...</h2><input name = \'message\' type=\'text\'><input type=\'submit\' value=\'Submit\'></form>'
			output += '</body></html>'
			self.wfile.write(output)
			return

		except:
			pass

# main will start server and use handler
def main():
	try:
		port = 8000
		# start server at this port with the handler defined above
		server = HTTPServer(('',port), webserverHandler)
		print ('Web server is running on port %s'%port)
		server.serve_forever()
	# stop serving when user input quits
	except KeyboardInterrupt:
		print (' (quit) entered; stopping web server...')
		server.socket.close()

# run main before ending script
if __name__ == '__main__':
	main()