from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# decipher messages sent by server
import cgi

# this is our handler that gets used when server is started in main()
class webserverHandler (BaseHTTPRequestHandler):
	# do_GET request handles all GET requests the server receives
	def do_GET(self):
		try:
			# check path (url sent by server as string)
			if self.path.endswith('/hello'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()	# blank line indicating end of headers
			
				# add some content to the response!
				output = ''
				output += '<html><body>Hello!'
				output += '<h2> Leave a message at the beep! </h2>'

				output += '<form method = \'POST\' enctype=\'multipart/form-data\' action=\'/hello\'><h2>beeeeeeeep . . . ...</h2><input name = \'message\' type=\'text\'><input type=\'submit\' value=\'Submit\'></form>'
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
		port = 8080
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