##Modified Sense Logger Example for MEGR3092
##measures sense hat sensors and GPS
#new comment

from datetime import datetime
import time
from sense_hat import SenseHat
from select import select
from threading import Thread

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
BASENAME = "Fall"
WRITE_FREQUENCY =100
ENABLE_CAMERA = False
LOG_AT_START = True

def hello():
	print("MEGR3092 Logger")
	print("Press Ctrl-C to stop.")


def file_setup(filename):
    header =[]

    header.append("GPS_Logger\ntime")

    if GPS_D:    
        header.extend(["GPSmph","GPStrack","GPSlat","GPSlong","GPSalt","GPSsats"])
    if TEMP_H:
        header.append("temp_h")
    if TEMP_P:
        header.append("temp_p")
    if HUMIDITY:
        header.append("humidity")
    if PRESSURE:
        header.append("pressure")
    if ORIENTATION:
        header.extend(["pitch","roll","yaw"])
    if MAG:
        header.extend(["mag_x","mag_y","mag_z"])
    if ACCELERATION:
        header.extend(["accel_x","accel_y","accel_z"])
    if GYRO:
        header.extend(["gyro_x","gyro_y","gyro_z"])

    with open(filename,"w") as f:
        f.write(",".join(str(value) for value in header)+ "\n")


## Function to collect data from the sense hat and build a string
def get_sense_data():
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
		#sense.set_pixel(7,0,whote)`
    
    if TEMP_H:
        sense_data.append(sense.get_temperature_from_humidity())

    if TEMP_P:
        sense_data.append(sense.get_temperature_from_pressure())

    if HUMIDITY:
        sense_data.append(sense.get_humidity())

    if PRESSURE:
        sense_data.append(sense.get_pressure())

    if ORIENTATION:
        yaw,pitch,roll = sense.get_orientation().values()
        sense_data.extend([pitch,roll,yaw])

    if MAG:
        mag_x,mag_y,mag_z = sense.get_compass_raw().values()
        sense_data.extend([mag_x,mag_y,mag_z])

    if ACCELERATION:
        x,y,z = sense.get_accelerometer_raw().values()
        sense_data.extend([x,y,z])

    if GYRO:
        gyro_x,gyro_y,gyro_z = sense.get_gyroscope_raw().values()
        sense_data.extend([gyro_x,gyro_y,gyro_z])

        return sense_data    


def log_data():
    output_string = ",".join(str(value) for value in sense_data)
    batch_data.append(output_string)


## Main Program
hello()
setgps10hz.main() #sends command to GPS to force 10hz for ublox hardware

#global gpsd #bring it in scope
gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    
sense = SenseHat()

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

                  
while run==True:
    ledrotate = 0;  
        
    sense_data = get_sense_data()
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
		
            filename = "log/"+"Log-"+str(localtime[0])+"-"+str(localtime[1])+"-"+str(localtime[2])+"-"+str(localtime[3])+"-"+str(localtime[4])+"-"+str(localtime[5])+".csv"
            file_setup(filename)

    if logging == True:
        sense_data = get_sense_data()
        log_data()


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
