
"""***************************************************************************************************
** ds18b20.py - Getting temperatures from multiple												   *
** DS18b20 temperature sensor																		*
******************************************************************************************************
** Author : Xavier Caron																			 *
** Version : 1.0																					 *
** based on Adafruit script																		  *
** https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software  *
**																								   *
** This script checks all ds18b20 sensor plugged to the Raspberry pi								 *
** and creates a raw csv file formatted as such :													*
** DATETIME ; SENSOR1 ; SENSOR2 ; ...																*
**																								   *
**																								   *
** Website : blog.biologeek.io																	   *
**																								   *
**																								   *
***************************************************************************************************
"""


import os
import glob
import datetime
import time
from PostgresDB import PostgresDB
from MySQLDB import MySQLDB


# Loading 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

PROJECT_DIR = "/var/lib/tomcat7/webapps/ROOT/"
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')
device_file = [f + '/w1_slave' for f in device_folder]
csv_to_write = PROJECT_DIR+"fic/ds18b20_raw_measurements.csv"

db_conf_file = PROJECT_DIR+"conf/db/mysql.conf"
db_table_name = "temperatures"

time_to_sleep = 0.2






mysql = MySQLDB (db_conf_file)
mysql.connect()
"""
postgres = PostgresDB (db_conf_file)
postgres.connect()
"""

def read_temp_raw():
	"""
		function read_temp_raw
		- IN : void
		- OUT : An array containing the lines of device_file

		This function loops over file lines and returns raw data
	"""
	i=0
	lines = [None]*len(device_file)

	# Looping over files list
	for file in device_file :
		f = open(file, 'r')
		lines[i] = f.readlines()
		i+=1
	
	print str(i)+" files read !"
	f.close()
	return lines

def read_temp():
	"""
		function read_temp
		- IN : void
		- OUT : An array containing all probes temperatures in degrees C

		This function loops over read files and searches for temperature values
	"""

	print "Reading files"
	file_lines = read_temp_raw()

	j=0

	temp_c=[None]*len(device_file)

	# While the probe is not ready, it sleeps for a little time and tries back
	while file_lines[0][0].strip()[-3:] != 'YES':
		time.sleep(time_to_sleep)
		file_lines = read_temp_raw()

	for lines in file_lines :
		# For each line we try to find the temperature value
		equals_pos = lines[1].find('t=')

		if equals_pos != -1 :
			print "Getting temperature"
			temp_string = lines[1][equals_pos+2:]
			temp_c[j] = float(temp_string) / 1000.0
		j+=1
	
	return temp_c


def write_temp_into_csv (data):
	"""
		function write_temp_into_csv
		- IN : data : String to write 
		- OUT : void
		This function writes data in csv file declared in the header csv_to_write
		If data != \n, it deletes the \n character
	"""

	w = open(csv_to_write, 'a')
	if (str (data) !="\n") :
		w.write(str(data).rstrip("\n"))
	else :
		w.write (str(data))
	w.close()

"""
def write_temp_into_mysql (date, uuid, probe, temperature):

	
		function write_temp_into_mysql
		- IN : date (current date), probe (current probe), temperature (current temperature)
		- OUT : void

		This function inserts a new entry in mysql table for probes (name defined in header)


	req = "INSERT INTO `"+db_table_name+"` (tmp_id, tmp_probe, tmp_probeuuid, tmp_date, tmp_rec_temp) VALUES ('', 'PROBE"+str(probe)+"', '"+uuid+"', '"+date+"', '"+temperature+"');"
	
	mysql.executeQuery (req)

	"""

def write_temp_into_postgres (date, uuid, probe, temperature):

	"""
		function write_temp_into_mysql
		- IN : date (current date), probe (current probe), temperature (current temperature)
		- OUT : void

		This function inserts a new entry in mysql table for probes (name defined in header)
	"""

	req = "INSERT INTO `"+db_table_name+"` (tmp_id, tmp_probe, tmp_probeuuid, tmp_date, tmp_rec_temp) VALUES ('', 'PROBE"+str(probe)+"', '"+uuid+"', '"+date+"', '"+temperature+"');"

	mysql.executeQuery (req)

	


print device_folder

while True:
	date = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
	temperatures = read_temp()
	print temperatures
	
	write_temp_into_csv(date)
	print temperatures

	i=0
	for temp in temperatures :

		probeUUID= os.path.basename(device_folder[i])
		
		write_temp_into_csv(';'+str(temp))
		#write_temp_into_mysql(date, probeUUId, i, temp)
	   	i+=1


	write_temp_into_csv("\n")

	time.sleep(1)

