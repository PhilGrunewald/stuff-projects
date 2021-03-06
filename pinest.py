#imports for thermometer reading
import os
import glob
import time
import datetime
#imports for gmail reading
import imaplib
import email
from db_phil import *     # reads the database and gmail information from db_phil.py
import MySQLdb

# wiringpi numbers  
import wiringpi2 as wiringpi
wiringpi.wiringPiSetup()
wiringpi.pinMode(0, 1) # sets WP pin 0 to output 

#Find temperature from thermometer
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd= dbPass, db=dbName)

def reconnect():
    dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd= dbPass, db=dbName)

def selectTemperture():
    nowTime = datetime.datetime.now().strftime('%H:%M:%S')
    sqlq = "SELECT temp FROM setTemp WHERE startTime < '%s' ORDER BY startTime DESC LIMIT 1;" % nowTime
    cursor = dbConnection.cursor()
    cursor.execute(sqlq)
    targetTemp = ("%s" % cursor.fetchone())
    cursor.close()
    return float(targetTemp)

def updateDatabase(setTemperature, room1Temperature):
    sqlq = "INSERT INTO temperature(setPoint, room1) \
            VALUES ('" + setTemperature + "', '" + room1Temperature + "');"
    cursor = dbConnection.cursor()
    cursor.execute(sqlq)
    dbConnection.commit()
    cursor.close()

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c #, temp_f

loopi = 0
while True:
        loopi += 1
        room1_temp =read_temp()
        print "Max room"
        print room1_temp
        try:
            set_temp = selectTemperture()
        except:
            set_temp = 19.1
            reconnect()
        print "Set temp"
        print set_temp
        if (loopi > 6):
            loopi = 0
            try:
                updateDatabase(str(set_temp), str(room1_temp))
            except:
                pass
        if (set_temp  > room1_temp):#Compare varSubject to temp
            wiringpi.digitalWrite(0, 0) # sets port 0 to 0 (3.3V, off) inverted from original - this is how my boiler works.
            print "HEATING ON\n"
        # Allow for a 1 degree window
        elif (room1_temp > set_temp + 1):
            wiringpi.digitalWrite(0, 1) # sets port 0 to 1 (3.3V, on)
            print "HEATING OFF\n"
        time.sleep(5)
