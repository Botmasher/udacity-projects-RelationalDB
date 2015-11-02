from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# decipher messages sent by server
import cgi

# pull out URL parameters
#from urlparse import urlparse, parse_qs

# sql and orm
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

# import restaurant db classes
from ormtest import Restaurant,MenuItem
engine = create_engine('sqlite:///restaurantmenu.db')

# start a session for CRUD actions
#Base.metadata.bind = engine 	# returning Base not defined
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
					output += '<a href = "/restaurants/%s/edit">edit</a> <a href = "/restaurants/delete">delete</a>'%r.id
				output += '</body></html>'
				# send an output stream message back to the client
				self.wfile.write(output)
				return

			elif self.path.endswith('/restaurants/new'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ''
				output += '<html><body>'
				output += '<h2> Add a new restaurant: </h2>'

				output += '<form method = \'POST\' enctype=\'multipart/form-data\' action=\'/restaurants\'><input name = \'add_new\' type=\'text\'><input type=\'submit\' value=\'Submit\'></form>'
				output += '</body></html>'
				self.wfile.write(output)
				return
			
			elif self.path.endswith('/edit'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				restaurant_id = self.path.split('/edit')[0].split('restaurants/')[1]
				this_r = session.query(Restaurant).filter(Restaurant.id==restaurant_id)[0]
				output = ''
				output += '<html><body>'
				output += '<h2>  Modify this restaurant: </h2>'

				output += '<form method="POST" enctype="multipart/form-data" action=""><input name="modify" type="text" value="'+this_r.name+'"><input type="submit" value="Submit"></form>'
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
				
				#added_restaurant = fields.get('add_new')[0]
				# store specific fields in array (using this_name from <input name="this_name">)
				if (fields.get('add_new') != None):
					added_restaurant = fields.get('add_new')[0]

					# now tell client what to do with info received
			
					# add restaurant to database
					new_restaurant = Restaurant (name=added_restaurant)
					session.add (new_restaurant)
					session.commit ()
					
					# format a page with user options
					output = ''
					output += '<html><body>'
					output += '<h2> Finished adding restaurant... </h2>'
					output += '<h1>%s</h1>'%added_restaurant
					#output += '<h1>%s</h1>'%mod_restaurant
					output += '<a href = "./new">Add another</a> <a href = "/restaurants">Home</a>'
					output += '</body></html>'
					self.wfile.write(output)
					return

				elif (fields.get('modify') != None):
					mod_restaurant = fields.get('modify')[0]
			
					# modify restaurant in database
					#updated_restaurant = Restaurantupdate(Restaurant).where(Restaurant.id==5).values(name=mod_restaurant)
					#session.save (updated_restaurant)
					#session.commit ()
					
					# format a page with user options
					output = ''
					output += '<html><body>'
					output += '<h2> Finished modifying restaurant... </h2>'
					output += '<h1>%s</h1>'%mod_restaurant
					output += '<a href = "/restaurants">Home</a>'
					output += '</body></html>'
					self.wfile.write(output)
					return

			#elif self.path.endswith('/delete'):

			#	output = '<html><body>'

			#	for i in parse_qs(urlparse(self.path).query):
			#		output += i

			#	output += '</body></html>'
			#	self.wfile.write(output)
			#	return

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