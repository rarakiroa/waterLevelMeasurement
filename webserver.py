from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import sqlite3
import json

PORT_NUMBER = 8080

conn = sqlite3.connect('dists.db')
c = conn.cursor()

class Distance(object):
	time = ""
	distance = ""

	def __init__(self, time, distance):
		self.time = time
		self.distance = distance

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		# Send the html message
		results = []
		for row in c.execute('SELECT * FROM distances WHERE distance < 200 OR distance > 225'):
			dist = Distance(row[0],row[1])
			results.append(dist)
		json_string = json.dumps([ob.__dict__ for ob in results])
		self.wfile.write(json_string)
		return

try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()

finally:
    conn.close()