#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import sqlite3

def writeToDB(distance):
	conn = sqlite3.connect('dists.db')
	c = conn.cursor()		
	
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='distances';")
	result = c.fetchone()

	if (result == None):
		print("Creating non-existing table distances")
		c.execute('''CREATE TABLE distances(time text, distance text)''')

	c.execute("INSERT INTO distances VALUES (\"" + str(time.time())  + "\"," + str(distance) + ")")
	conn.commit()
	conn.close()

def measureDistanceToWater(putInDB):
	try:
		GPIO.setmode(GPIO.BOARD)

		PIN_TRIGGER = 7
		PIN_ECHO = 11

		GPIO.setup(PIN_TRIGGER, GPIO.OUT)
		GPIO.setup(PIN_ECHO, GPIO.IN)

		GPIO.output(PIN_TRIGGER, GPIO.LOW)

		print "Waiting for sensor to settle"

		time.sleep(2)

		distances = []
		i = 0
		while i < 10:
			print "Measuring distance"

			GPIO.output(PIN_TRIGGER, GPIO.HIGH)

			time.sleep(0.1)

			GPIO.output(PIN_TRIGGER, GPIO.LOW)

			while GPIO.input(PIN_ECHO)==0:
				pulse_start_time = time.time()
			while GPIO.input(PIN_ECHO)==1:
				pulse_end_time = time.time()

			pulse_duration = pulse_end_time - pulse_start_time
			distance = round(pulse_duration * 17150, 2)
			print "Distance:",distance,"cm"
			distances.append(distance)
			i = i + 1

		sum = 0
		for d in distances:
			sum = sum + d
		
		average = sum / 10

		if putInDB:
			writeToDB(average)

	finally:
		GPIO.cleanup()

measureDistanceToWater(True)