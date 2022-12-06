
##Modified Sense Logger Example for MEGR3092
##measures sense hat sensors and GPS
#threading attempt

from datetime import datetime
import time
from select import select
import threading 

#import sensors
from sense_hat import SenseHat
from gps import *
import setgps10hz  ## sets ublox gps receiver to 10 hz

#from time import *
global gpsd

## Logging Settings
GPS_D=True
TEMP_H=True
TEMP_P=True
HUMIDITY=True
PRESSURE=True
ORIENTATION=True
ACCELERATION=True
MAG=True
GYRO=True
DELAY = 0
BASENAME = "Fall"
WRITE_FREQUENCY =2
ENABLE_CAMERA = False
LOG_AT_START = True

global sense_data
global sense_data2

def hello():
	print("MEGR3092 Logger")
	print("Press Ctrl-\ to stop.")

def file_setup1(filename):
    header =[]

    header.append("GPS_Logger\ntime")

    if GPS_D:    
        header.extend(["GPSmph","GPStrack","GPSlat","GPSlong","GPSalt","GPSsats"])

    with open(filename,"w") as f:
        f.write(",".join(str(value) for value in header)+ "\n")

def file_setup2(filename2):
    header2 =[]

    header2.append("sensehat_Logger\ntime")

    if TEMP_H:
        header2.append("temp_h")
    if TEMP_P:
        header2.append("temp_p")
    if HUMIDITY:
        header2.append("humidity")
    if PRESSURE:
        header2.append("pressure")
    if ORIENTATION:
        header2.extend(["pitch","roll","yaw"])
    if MAG:
        header2.extend(["mag_x","mag_y","mag_z"])
    if ACCELERATION:
        header2.extend(["accel_x","accel_y","accel_z"])
    if GYRO:
        header2.extend(["gyro_x","gyro_y","gyro_z"])

    with open(filename2,"w") as g:
        g.write(",".join(str(value) for value in header2)+ "\n")



## Function to collect data from the gps and build a string
def get_gps_data():
    localtime = datetime.now()
    ##current_time = str(localtime.hour)+":"+str(localtime.minute)+":"+str(localtime.second)+"."+str(localtime.microsecond)
    current_time = str(datetime.now().time()) ## for simplified mega log viewer 
    ##current_time = time.time() ## for mclaren atlas
    log_string = current_time[:-3] ##strip last three time decimals to keep atlas happy

    sense_data=[]
    sense_data.append(log_string)  ##moved timestamp to beginning for megalogviewer compatability
    
    if GPS_D:
                gpsd.next()  #get the latest GPS data from GPSD
                sense_data.append(gpsd.fix.speed*2.236)#m/s converted to mph
                sense_data.append(gpsd.fix.track)
                sense_data.append(gpsd.fix.latitude)
                sense_data.append(gpsd.fix.longitude)
                sense_data.append(gpsd.fix.altitude)
                #sense_data.append(gpsd.fix.sats)
                sense_data.append("sats")
		
                print 'speed (mph) ' , gpsd.fix.speed*2.236,"           \r",
	
		
		return sense_data

def get_hat_data():
    localtime = datetime.now()
    ##current_time = str(localtime.hour)+":"+str(localtime.minute)+":"+str(localtime.second)+"."+str(localtime.microsecond)
    current_time = str(datetime.now().time()) ## for simplified mega log viewer 
    ##current_time = time.time() ## for mclaren atlas
    log_string = current_time[:-3] ##strip last three time decimals to keep atlas happy

    sense_data2=[]
    sense_data2.append(log_string)  ##moved timestamp to beginning for megalogviewer compatability

    if TEMP_H:
        sense_data2.append(sense.get_temperature_from_humidity())

    if TEMP_P:
        sense_data2.append(sense.get_temperature_from_pressure())

    if HUMIDITY:
        sense_data2.append(sense.get_humidity())

    if PRESSURE:
        sense_data2.append(sense.get_pressure())

    if ORIENTATION:
        yaw,pitch,roll = sense.get_orientation().values()
        sense_data2.extend([pitch,roll,yaw])

    if MAG:
        mag_x,mag_y,mag_z = sense.get_compass_raw().values()
        sense_data2.extend([mag_x,mag_y,mag_z])

    if ACCELERATION:
        x,y,z = sense.get_accelerometer_raw().values()
        sense_data2.extend([x,y,z])

    if GYRO:
        gyro_x,gyro_y,gyro_z = sense.get_gyroscope_raw().values()
        sense_data2.extend([gyro_x,gyro_y,gyro_z])
	
	return sense_data2    
		


def log_data1():
    output_string1 = ",".join(str(value) for value in sense_data)
    batch_data.append(output_string1)
	
def log_data2():
    output_string2 = ",".join(str(value) for value in sense_data2)
    batch_data2.append(output_string2)
	
def timed_log1():
    while run:
        if logging == True:
            log_data1()
        time.sleep(DELAY)
	
def timed_log2():
    while run:
        if logging == True:
	    log_data2()
        time.sleep(DELAY)


	
def gpsthread():

	
	run=True
	running = False
	logging_event = True
	logstate = False
	logging=LOG_AT_START
	#show_state(logging)
	batch_data= []

	#for new filenames each command
	#filename = "log/"+"Log-"+str(datetime.now())+".csv"
	#file_setup(filename)

	if DELAY > 0:
	    Thread(target= timed_log1).start()


	while run==True:

	    sense_data = get_gps_data()
	    #gpsd.next()  #get the latest GPS data from GPSD help with delays

	    #logging_event,run = check_inputj() # causes a crash
	    #logging_event = logging

	    if logging_event and logging:
		    logging = False

	    elif logging_event :
		    logging_event = False
		    logging = True
		    #for new file names each run
		    localtime = time.localtime(time.time())

		    filename = "log/"+"Log-"+str(localtime[0])+"-"+str(localtime[1])+"-"+str(localtime[2])+"-"+str(localtime[3])+"-"+str(localtime[4])+"-"+str(localtime[5])+"1"+".csv"
		    file_setup1(filename)

	    if logging == True and DELAY == 0:
		sense_data = get_gps_data()
		log_data1()


	    if len(batch_data) >= WRITE_FREQUENCY:
		with open(filename,"a") as f:
		    for line in batch_data:
			f.write(line + "\n")
		    batch_data = []

	try:
	    with open(filename,"a") as f:
		for line in batch_data:
			f.write(line + "\n")
			batch_data = []
			print(".")
	except:
		print("No log file to close")
		time.sleep(1)
	

def hatthread():

	run=True
	running = False
	logging_event = True
	logstate = False
	logging=LOG_AT_START
	batch_data2= []

	#for new filenames each command
	#filename = "log/"+"Log-"+str(datetime.now())+".csv"
	#file_setup(filename)

	if DELAY > 0:
	    Thread(target= timed_log2).start()


	while run==True:


	    sense_data2 = get_hat_data()	


	    #logging_event,run = check_inputj() # causes a crash
	    #logging_event = logging

	    if logging_event and logging:
		    logging = False

	    elif logging_event :
		    logging_event = False
		    logging = True
		    #for new file names each run
		    localtime = time.localtime(time.time())

		    filename2 = "log/"+"Log-"+str(localtime[0])+"-"+str(localtime[1])+"-"+str(localtime[2])+"-"+str(localtime[3])+"-"+str(localtime[4])+"-"+str(localtime[5])+"2"+".csv"
		    file_setup2(filename2)

	    if logging == True and DELAY == 0:
		sense_data2 = get_hat_data()
		log_data2()


	    if len(batch_data2) >= WRITE_FREQUENCY:
		with open(filename2,"a") as g:
		    for line in batch_data2:
			g.write(line + "\n")
		    batch_data2 = []

	try:
	    with open(filename2,"a") as g:
		for line in batch_data2:
			g.write(line + "\n")
			batch_data2 = []
			print(".")
	except:
		print("No log file to close")
		time.sleep(1)	
hello()
setgps10hz.main() #sends command to GPS to force 10hz for ublox hardware

#global gpsd #bring it in scope
gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info


sense = SenseHat()

batch_data= []
batch_data2= []

a = threading.Thread(target= gpsthread, name='GPS data thread')
daemon = True
b = threading.Thread(target= hatthread, name='Sense hat data thread')
daemon = True
a.start()
b.start()	
	
