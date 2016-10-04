#!/usr/bin/env python

import obd_io
import serial
import platform
import obd_sensors
from datetime import datetime
import time
import getpass
import RPi.GPIO as GPIO

from obd_utils import scanSerial

switchpin = 37
ledpin = 33

GPIO.setmode(GPIO.BOARD)
GPIO.setup(switchpin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(40, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(ledpin, GPIO.OUT)
#loggingEnable


def doLogger(channel):
        global loggingEnable
        if GPIO.input(switchpin):
            print("Logging Disabled")
            GPIO.output(ledpin, GPIO.LOW)
            loggingEnable = False
        else: 
            print("Logging Enabled")
            GPIO.output(ledpin, GPIO.HIGH)
            loggingEnable = True

GPIO.add_event_detect(switchpin, GPIO.BOTH, callback=doLogger, bouncetime=300)

class OBD_Recorder():
    def __init__(self, path, log_items):
        self.port = None
        self.sensorlist = []
        localtime = time.localtime(time.time())
        filename = path+"car-"+str(localtime[0])+"-"+str(localtime[1])+"-"+str(localtime[2])+"-"+str(localtime[3])+"-"+str(localtime[4])+"-"+str(localtime[5])+".log"
        self.log_file = open(filename, "w", 128)
        self.log_file.write("Time,RPM,MPH,Throttle,Load,Fuel Status\n");

        for item in log_items:
            self.add_log_item(item)

        self.gear_ratios = [34/13, 39/21, 36/23, 27/20, 26/21, 25/22]
        #log_formatter = logging.Formatter('%(asctime)s.%(msecs).03d,%(message)s', "%H:%M:%S")

    def connect(self):
        portnames = scanSerial()
        #portnames = ['COM10']
        print portnames
        for port in portnames:
            self.port = obd_io.OBDPort(port, None, 2, 2)
            if(self.port.State == 0):
                self.port.close()
                self.port = None
            else:
                break

        if(self.port):
            print "Connected to "+self.port.port.name
            
    def is_connected(self):
        return self.port
        
    def add_log_item(self, item):
        for index, e in enumerate(obd_sensors.SENSORS):
            if(item == e.shortname):
                self.sensorlist.append(index)
                print "Logging item: "+e.name
                break
            
            
    def record_data(self):
        if(self.port is None):
            return None
        
        print "Logging started"
        
        while 1:
            localtime = datetime.now()
            current_time = str(localtime.hour)+":"+str(localtime.minute)+":"+str(localtime.second)+"."+str(localtime.microsecond)
            log_string = current_time
            results = {}
            for index in self.sensorlist:
                (name, value, unit) = self.port.sensor(index)
                log_string = log_string + ","+str(value)
                results[obd_sensors.SENSORS[index].shortname] = value;

            gear = self.calculate_gear(results["rpm"], results["speed"])
            log_string = log_string #+ "," + str(gear)
            self.log_file.write(log_string+"\n")

            
    def calculate_gear(self, rpm, speed):
        if speed == "" or speed == 0:
            return 0
        if rpm == "" or rpm == 0:
            return 0

        rps = rpm/60
        mps = (speed*1.609*1000)/3600
        
        primary_gear = 85/46 #street triple
        final_drive  = 47/16
        
        tyre_circumference = 1.978 #meters

        current_gear_ratio = (rps*tyre_circumference)/(mps*primary_gear*final_drive)
        
        #print current_gear_ratio
        gear = min((abs(current_gear_ratio - i), i) for i in self.gear_ratios)[1] 
        return gear
        
username = getpass.getuser()  
logitems = ["rpm", "speed", "throttle_pos", "load", "fuel_status"]
#o = OBD_Recorder('/home/'+username+'/pyobd-pi/log/', logitems) #had to hard code directory for auto run
o = OBD_Recorder('/home/pi/pyobd-pi/log/', logitems)
o.connect()
loggingEnable = False

while True:
    if loggingEnable:
        print "trying to log"
        try:
            if not o.is_connected():
                print "Not connected"                
            print('logging')
	    o.record_data()

        except:
            print "exception - likely no car found"
    time.sleep(1)
    print "looping"

GPIO.remove_event_detect(switchpin)
GPIO.cleanup()
self.log_file.close
