#!/usr/bin/python

import sys
import os
import sqlite3
from engineClasses.tools import tools


myTool = tools()
firstArg = 0
silent = 0

if "-s" in sys.argv or "--silent" in sys.argv:
    silent = 1

# copy database template
os.system("rm data/mergedData.db")
os.system("cp data/dataTemplate.db data/mergedData.db")

# connect to final database
connection = sqlite3.connect("data/mergedData.db")
connectionCursor = connection.cursor()

if silent == 0:
    print myTool.green + "[+] " + myTool.stop + "Merging database files"
    print ""

# go through all database files
for argument in sys.argv:
    if firstArg == 0 or argument == "-s" or argument == "--silent":
        firstArg = 1
        continue
    if silent == 0:
        print myTool.green + "[+] " + myTool.stop + argument
    connectionCurrent = sqlite3.connect("data/merge/" + argument)
    connectionCursorCurrent = connectionCurrent.cursor()
    # get all location entries of the current database file
    connectionCursorCurrent.execute("select * from locations")
    allLocations = connectionCursorCurrent.fetchall()	    
    # save them with all other items to the final database
    for location in allLocations:
        # look if location is already in final database file
        connectionCursor.execute("select * from locations where country=\"" + str(location[1]) + "\" and zipcode=\"" + str(location[2]) + "\" and city=\"" + str(location[3]) + "\" and street=\"" + str(location[4]) + "\" and streetnumber=\"" + str(location[5]) + "\"")
        inDatabase = connectionCursor.fetchall()
        # location not in final database
        if len(inDatabase) == 0:
            if silent == 0:
                print myTool.green + "[+]\t" + myTool.stop + " Adding location..."
            
            # insert new location to final database
            connectionCursor.execute("insert into locations (country, zipcode, city, street, streetnumber, gpsl, gpsw, time) values (\"" + str(location[1]) + "\", \"" + str(location[2]) + "\", \"" + str(location[3]) + "\", \"" + str(location[4]) + "\", \"" + str(location[5]) + "\", \"" + str(location[6]) + "\", \"" + str(location[7]) + "\", \"" + str(location[8]) + "\")")
            connection.commit()

            # get the last location ID
            connectionCursor.execute("select ID from locations order by ID desc limit 1")
            thisID = connectionCursor.fetchall()[0][0]    
        # location already in final database
        else:
            if silent == 0:
                print myTool.green + "[+]\t" + myTool.stop + " Using location..."
            # do not insert location to database and save the location ID
            thisID = inDatabase[0][0]
        idLocalFile = location[0]
        # insert all corresponding entries
        connectionCursorCurrent.execute("select * from accesspoints where locationId=\"" + str(idLocalFile) + "\"")
        currentAPs = connectionCursorCurrent.fetchall()
        if silent == 0:
            print myTool.green + "[+]\t\t" + myTool.stop + "Adding access points..."
        for AP in currentAPs:        
            connectionCursor.execute("insert into accesspoints (bssid, essid, channel, power, locationId, encryption, time) values (\"" + str(AP[1]) + "\", \"" + u''.join(AP[2]).encode('utf-8') + "\", \"" + str(AP[3]) + "\", \"" + str(AP[4]) + "\", \"" + str(thisID) + "\", \"" + str(AP[6]) + "\", \"" + str(AP[7]) + "\")")
            connection.commit()
        connectionCursorCurrent.execute("select * from clientProbes where locationId=\"" + str(idLocalFile) + "\"")
        currentCPs = connectionCursorCurrent.fetchall()
        if silent == 0:
            print myTool.green + "[+]\t\t" + myTool.stop + "Adding client probes..."
        for CP in currentCPs:        
            connectionCursor.execute("insert into clientProbes (clientMac, probe, locationId, power, timeFirst, timeLast) values (\"" + str(CP[1]) + "\", \"" + u''.join(CP[2]).encode('utf-8') + "\", \"" + str(thisID) + "\", \"" + str(CP[4]) + "\", \"" + str(CP[5]) + "\", \"" + str(CP[6]) + "\")")
            connection.commit()
        connectionCursorCurrent.execute("select * from connections where locationId=\"" + str(idLocalFile) + "\"")
        currentCs = connectionCursorCurrent.fetchall()
        if silent == 0:
            print myTool.green + "[+]\t\t" + myTool.stop + "Adding connections..."
        for C in currentCs:
            connectionCursor.execute("insert into connections (macOne, macTwo, power, locationId, timeFirst, timeLast) values (\"" + str(C[1]) + "\", \"" + str(C[2]) + "\", \"" + str(C[3]) + "\", \"" + str(thisID) + "\", \"" + str(C[5]) + "\", \"" + str(C[6]) + "\")")
            connection.commit() 
        if silent == 0:
            print ""

connection.close()
print myTool.green + "[+]" + myTool.stop + " The mergedData.db saved to data/ folder."