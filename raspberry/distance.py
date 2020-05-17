# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import thingspeak
import argparse

#GPIO mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#GPIO pins
GPIO_TRIGGER = 7
GPIO_ECHO = 11

parser = argparse.ArgumentParser()
parser.add_argument('--channelId', dest='channelId',help='Thingspeak channel id',required=True)
parser.add_argument('--readKey', dest='readKey',help='Thingspeak read key',required=True)
parser.add_argument('--writeKey', dest='writeKey',help='Thingspeak write key',required=True)
args = parser.parse_args()


maximum_distance = 156


#Direction of the pins (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def measureDistance():
    
    GPIO.output(GPIO_TRIGGER, True)
 
    
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    startTime = time.time()
    stopTime = time.time()
 
    # Start time
    while GPIO.input(GPIO_ECHO) == 0:
        startTime = time.time()
 
    # Receving signal time
    while GPIO.input(GPIO_ECHO) == 1:
        stopTime = time.time()
 
    # Difference between start and end
    TimeElapsed = stopTime - startTime

    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    channel = thingspeak.Channel(id=args.channelId, write_key=args.writeKey, api_key=args.readKey)
    try:
        while True:
            currentDistance = measureDistance()
            height = maximum_distance - currentDistance
            t = time.localtime()
            current_time = time.strftime("%d.%m.%Y %H:%M:%S", t)
            # we know that the tank hast to have a distance of more than 10cm
            if currentDistance > 10:
                print ("%s: Measured distance = %.1f cm" % (current_time, currentDistance))
                try:
                    response = channel.update({'field1': height })
                except:
                    print ("%s: No CONNECTION! Measured distance = %.1f cm" % (current_time, currentDistance))
                print ("%s: Height = %.1f cm" % (current_time, height))
            else:
                print ("%s: Distance was to low... (%.1f cm)" % (current_time, currentDistance))
            time.sleep(360)
 

    except KeyboardInterrupt:
        print("Stopped by user!")
    finally:
        GPIO.cleanup()
