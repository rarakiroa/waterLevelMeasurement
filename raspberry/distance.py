# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import thingspeak
import argparse

#GPIO mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#GPIO pins
GPIO_TRIGGER = 4
GPIO_ECHO = 17

parser = argparse.ArgumentParser()
parser.add_argument('--channelId', dest='channelId',help='Thingspeak channel id',required=True)
parser.add_argument('--readKey', dest='readKey',help='Thingspeak read key',required=True)
parser.add_argument('--writeKey', dest='writeKey',help='Thingspeak write key',required=True)
args = parser.parse_args()


maximum_distance = 156
wait_time = 60 * 10

#Direction of the pins (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(7,GPIO.OUT)

def log(message):
    t = time.localtime()
    current_time = time.strftime("%d.%m.%Y %H:%M:%S", t)
    print("%s: %s" % (current_time, message))
 
def blink(short, times):
    sleep_time = (1,0.3)[short]
    for i in range(0, times):
        GPIO.output(7,GPIO.LOW)
        time.sleep(sleep_time)
        GPIO.output(7,GPIO.HIGH)
        time.sleep(sleep_time)

def measureDistance():
    
    GPIO.output(GPIO_TRIGGER, True)
 
    
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
    startTime = time.time()
    stopTime = time.time()
    log("Sending signal")
    # Start time
    while GPIO.input(GPIO_ECHO) == 0:
        startTime = time.time()
    log("Waiting for response")
    # Receving signal time
    while GPIO.input(GPIO_ECHO) == 1:
        stopTime = time.time()
    log("Received signal")
    # Difference between start and end
    TimeElapsed = stopTime - startTime

    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    channel = thingspeak.Channel(id=args.channelId, write_key=args.writeKey, api_key=args.readKey)
    GPIO.output(7,GPIO.HIGH)
    try:
        while True:
            print("#########")
            blink(short=True, times=2)
            currentDistance = measureDistance()
            height = maximum_distance - currentDistance
            t = time.localtime()
            current_time = time.strftime("%d.%m.%Y %H:%M:%S", t)
            # we know that the tank hast to have a distance of more than 10cm
            if currentDistance > 10 and height > 0:
                print ("%s: Measured distance = %.1f cm" % (current_time, currentDistance))
                try:
                    log("Uploading data...")
                    response = channel.update({'field1': height })
                    blink(True, 3)
                except:
                    print ("%s: No CONNECTION! Measured distance = %.1f cm" % (current_time, currentDistance))
                print ("%s: Height = %.1f cm" % (current_time, height))
            else:
                print ("%s: Distance was to low... (%.1f cm)" % (current_time, currentDistance))
            time.sleep(wait_time)
 

    except KeyboardInterrupt:
        log("Stopped by user!")
    finally:
        GPIO.output(7,GPIO.LOW)
        GPIO.cleanup()
