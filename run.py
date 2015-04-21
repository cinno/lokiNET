#!/usr/bin/python


from engineClasses.tools import tools
import os
import sys
import signal
import time
import sqlite3
import urllib2


myTool = tools()
usageString = "Usage: " + sys.argv[0] + myTool.blue  + " <interface> <options>" + myTool.stop
invalidString = myTool.fail + "[-]" + myTool.stop + " Invalid parameter combination!"
offlineOrOnline = "offline"
gpsOrStreet = "address"
currentTimestamp = time.time()
interface = sys.argv[1]
dataFile = "Data.db"


def createDatabaseFile(sig):
	# check if copy file already exists
	if os.path.isfile("data/" +  sig + dataFile):
		pass
	else:
		os.system("cp data/dataTemplate.db data/" + sig + dataFile)	

def ctrlc_handler(self, frm):
        if "-m" in sys.argv or "--monitor" in sys.argv:
                print myTool.green + "[+] " + myTool.stop + "Monitor mode removed"
                os.system("ifconfig " + interface + " down")
                os.system("iwconfig " + interface + " mode managed")
                os.system("ifconfig " + interface + " up")
        print myTool.green + "\n\n[+] " + myTool.stop + "Good bye!"
        print "*** Remember: \"A hacker should only be limited by his imagination and not by his tools.\"\n"
        sys.exit(0)

if len(sys.argv) < 2:
        sys.exit(usageString + "\n-h: help menu")
else:
        signal.signal(signal.SIGINT, ctrlc_handler)

	# help menu
        if "-h" in sys.argv or "--help" in sys.argv:
                print usageString
                print "scanengine:" + myTool.blue + "\t[-addr|--address]" + myTool.stop + "\t" + myTool.green + "[default] " + myTool.stop + "Use direct address input for location (excludes GPS input)"
                print myTool.blue + "\t\t[-gps|--gps]" + myTool.stop + "\t\tUse direct GPS input for location (excludes address input)"
                print myTool.blue + "\t\t[-off|--offline]" + myTool.stop + "\t" + myTool.green + "[default]" + myTool.stop + "Uses offline mode (excludes online mode)"
                print myTool.blue + "\t\t[-on|--online]" + myTool.stop + "\t\tUse online mode (excludes offline mode)"

                print "webinterface:" +  myTool.blue + "\t[-web|--webinterface]" + myTool.stop + "\tStart webserver to analyse collected data"

                print "others:" + myTool.blue + "\t\t[-h|--help]" + myTool.stop + "\t\tPrints this help menu"
                print myTool.blue + "\t\t[-m|--monitor]" + myTool.stop + "\t\tChange mode of selected interface to \"monitor\" "
                print ""
                sys.exit()

	# start monitor mode if desired
        if "-m" in sys.argv or "--monitor" in sys.argv:
                os.system("ifconfig " + interface + " down")
                os.system("iwconfig " + interface + " mode monitor")
                os.system("ifconfig " + interface + " up")
                print myTool.green + "[+] " + myTool.stop + "Monitor interface started."

	# start evaluation webinterface
        if "-web" in sys.argv or "--webinterface" in sys.argv:
		signature = raw_input("# Session value: ")
		connection = sqlite3.connect("data/" + signature + "Data.db")
		connectionCursor = connection.cursor()
		statement = "select * from locations"
		try:
			connectionCursor.execute(statement)
			result = connectionCursor.fetchall()			
			print myTool.green + "[+] " + myTool.stop + "Starting webinterface for database analysis. You should point your browser to:"
			print myTool.green + "[+]" + myTool.stop + " http://127.0.0.1:8000/cgi-bin/index.html"
			os.system("python -m CGIHTTPServer")
			sys.exit()
		except:
			print myTool.fail + "[-] " + myTool.stop + "Webserver could not be started!"
			print myTool.fail + "[-] " + myTool.stop + "Database file does not exists or is empty."
			print myTool.fail + "[-] " + myTool.stop + "Collect some data first..."
			sys.exit()

	# use offline mode
        if "-off" in sys.argv or "--offline" in sys.argv:
                # check for invalid option
                if "-on" in sys.argv or "--online" in sys.argv:
                        sys.exit(invalidString)
                else:
                        print myTool.green + "[+]" + myTool.stop + " Offline mode selected."
                        offlineOrOnline = "offline"

        # use online mode
        if "-on" in sys.argv or "--online" in sys.argv:
                # check for invalid option
                if "-off" in sys.argv or "--offline" in sys.argv:
                        sys.exit(invalidString)
                else:
                        print myTool.green + "[+]" + myTool.stop + " Online mode selected."
                        offlineOrOnline = "online"

	# direct gps input
        if "-gps" in sys.argv or "--gps" in sys.argv:
                # check for invalid option
                if "-addr" in sys.argv or "--address" in sys.argv:
                        sys.exit(invalidString)
                else:
                        print myTool.green + "[+]" + myTool.stop + " GPS mode selected."
                        gpsOrStreet = "gps"

        # address input (convert to to gps later)
        if "-addr" in sys.argv or "--address" in sys.argv:
                # check for invalid option
                if "-gps" in sys.argv or "--gps" in sys.argv:
                        sys.exit(invalidString)
                else:
                        print myTool.green + "[+]" + myTool.stop + " Address mode selected."
                        gpsOrStreet = "address"

	# start session
	if gpsOrStreet == "address":
		print myTool.green + "\n[+++] " + myTool.stop + "Scanengine Selected" + myTool.green + " [+++]" + myTool.stop
		print "[?] Type in your current location:"
		country = raw_input("# Country: ")
		zipcode = raw_input("# Zipcode: ")
		city = raw_input("# City: ")
		street = raw_input("# Street: ")
		streetnumber = raw_input("# Streetnumber: ")
		print "[?] Type in the session id:"
		signature = raw_input("# Session value: ")
		
		createDatabaseFile(signature)
		
		# save new location to database
		connection = sqlite3.connect("data/" + signature + "Data.db")
		connectionCursor = connection.cursor()

		if offlineOrOnline == "offline":
			statement = "insert into locations (country, zipcode, city, street, streetnumber, gpsl, gpsw, time) values (\"" + country + "\", \"" + zipcode + "\", \"" + city + "\", \"" + street + "\", \"" + streetnumber + "\", \"0\", \"0\", \"" + str(currentTimestamp) + "\")"
		else:
			# resolve gps coordinates from address
			url = "http://maps.googleapis.com/maps/api/geocode/xml?address=" + urllib2.quote(country) + ",+" + urllib2.quote(zipcode) + ",+" + urllib2.quote(city) + ",+" + urllib2.quote(street) + ",+" + urllib2.quote(streetnumber) + "&sensor=false"
			# extract GPS coordinates
			res = myTool.streetToGps(url)
			statement = "insert into locations (country, zipcode, city, street, streetnumber, gpsl, gpsw, time) values (\"" + country + "\", \"" + zipcode + "\", \"" + city + "\", \"" + street + "\", \"" + streetnumber + "\", \"" + res[1] + "\", \"" + res[0] + "\", \"" + str(currentTimestamp) + "\")"
			print myTool.green + "[+] " + myTool.stop + "Resolving GPS coordinates... (needs internet connection!)"
			
		connectionCursor.execute(statement)
		connection.commit()    		
		
		statement = "SELECT ID FROM locations ORDER BY ID DESC LIMIT 1"
		connectionCursor.execute(statement)
		maxLocationId = connectionCursor.fetchall()[0][0]
		
		# execute scan script
		os.system("./scan.py " + interface + " " + signature + " " + str(maxLocationId))