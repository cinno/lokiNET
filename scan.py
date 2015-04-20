#!/usr/bin/python

import sys
import os
from engineClasses.tools import tools
from scapy.all import *
import sqlite3
import time
import datetime

 
myTool = tools()
clientProbes = set()
currentTimestamp = time.time()
currentDateAndTime = datetime.datetime.fromtimestamp(currentTimestamp).strftime("%Y-%m-%d %H:%M:%S")

interface = sys.argv[1]
signature = sys.argv[2]
dataFile = signature + "Data.db"
locationID = int(sys.argv[3])


def dbChangeCommit(statement):
	connectionCursor.execute(statement)
	connection.commit()	

def extractTransmissionPower(packet):
	power = "0"

	try:
		power = packet.getlayer(RadioTap).notdecoded
		power = power.split(" ")
		power = str(int(power[0][len(power)-5:len(power)-4:].encode("hex"), 16))
	except:
		power = "0"
		print myTool.warning + "[!] " + myTool.stop + "Extracting transmission power failed..."

        return power


def pktHandler(pkt):
	# scan for probe requests
	if pkt.haslayer(Dot11ProbeReq):
		curSSID = "[broadcast]"
   
 		if len(pkt.getlayer(Dot11ProbeReq).info) > 0:
			curSSID = pkt.getlayer(Dot11ProbeReq).info

		newCombination = pkt.getlayer(Dot11).addr2 + " " + curSSID
		if newCombination not in clientProbes:
			clientProbes.add(newCombination)

			# extract transmission power
			power = extractTransmissionPower(pkt)
    
			print myTool.green + "[+] " + myTool.stop + str(currentDateAndTime) + ": Discovered new unique probe request (" + str(len(clientProbes)) + "): "
			print myTool.green + "[+] " + myTool.stop + "MAC --> " + pkt.getlayer(Dot11).addr2 
			print myTool.green + "[+] " + myTool.stop + "probe --> " + curSSID
			print myTool.green + "[+] " + myTool.stop + "power --> " + power
			print ""

			# save tupel to database
			dbChangeCommit("insert into clientProbes (clientMac, probe, locationId, power, timeFirst, timeLast) values (\"" + pkt.getlayer(Dot11).addr2 + "\", \"" + curSSID + "\", \"" + str(locationID) + "\", \"" + power + "\", \"" + str(currentTimestamp) + "\", \"" + str(currentTimestamp) + "\")")
		else:
			# update last seen parameter
			dbChangeCommit("UPDATE clientProbes SET timeLast='" + str(currentTimestamp) + "' WHERE clientMac='" + pkt.getlayer(Dot11).addr2 + "' AND probe='" + curSSID + "'")

# connect to local database file
connection = sqlite3.connect("data/" + dataFile)
connectionCursor = connection.cursor()

# channel hopping
channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
while True:
	for i in channels:
		os.system("iw dev " + sys.argv[1] + " set channel " + str(i))

		currentTimestamp = time.time()
		currentDateAndTime = datetime.datetime.fromtimestamp(currentTimestamp).strftime("%Y-%m-%d %H:%M:%S")
                        
		pkt = sniff(iface=interface, count=1, prn=pktHandler)
connection.close()
sys.exit(0)
