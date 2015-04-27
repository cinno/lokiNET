#!/usr/bin/python

########################################################################
# Copyright 2015 Daniel Haake
#
# This file is part of lokiNET
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################

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
ssids = set()
clientAPSet = set()


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
	# scan for datapackets
	if pkt.haslayer(Dot11):
		curPkt = pkt.getlayer(Dot11)
		if curPkt.type == long(2L):
			if curPkt.addr1 != "ff:ff:ff:ff:ff:ff" and curPkt.addr2 != "ff:ff:ff:ff:ff:ff" and curPkt.addr2 != "00:00:00:00:00:00" and curPkt.addr1 != "00:00:00:00:00:00":
				comb1 = curPkt.addr1 + " " + curPkt.addr2
				comb2 = curPkt.addr2 + " " + curPkt.addr1
				if comb1 not in clientAPSet and comb2 not in clientAPSet:
					clientAPSet.add(comb1)
					clientAPSet.add(comb2)
	
					# extract transmission power
					power = extractTransmissionPower(pkt)
	
					print myTool.green + "[+] " + myTool.stop + str(currentDateAndTime) + ": Data exchange between " + curPkt.addr1 + " and " + curPkt.addr2 + " (" + str(int(len(clientAPSet)/2)) + "):"
					print myTool.green + "[+] " + myTool.stop + "power --> " + power
					print ""
	
					# save tupel data to database
					dbChangeCommit("insert into connections (macOne, macTwo, power, locationId, timeFirst, timeLast) values (\"" + curPkt.addr1 + "\", \"" + curPkt.addr2 + "\", \"" + power + "\", \"" + str(locationID) + "\", \"" + str(currentTimestamp) + "\", \"" + str(currentTimestamp) +  "\")")
				else:
					dbChangeCommit("UPDATE connections SET timeLast='" + str(currentTimestamp) + "' WHERE macOne='" + curPkt.addr1 + "' AND macTwo='" + curPkt.addr2 + "'")					
					dbChangeCommit("UPDATE connections SET timeLast='" + str(currentTimestamp) + "' WHERE macOne='" + curPkt.addr2 + "' AND macTwo='" + curPkt.addr1 + "'")

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

	# scan for accesspoints
	if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
		currSSID = "dummy"
		channel = "null"
		temp = pkt
		while temp:
			temp = temp.getlayer(Dot11Elt)
			bssidEssidPair = pkt.getlayer(Dot11).addr3 + " " + temp.info
			if temp and (temp.ID == 0 or temp.ID == 3) and bssidEssidPair not in ssids and temp.info:
				# extract channel, print output and save it to database
				if temp.ID == 3 and currSSID != "dummy":
					# extract transmission power
					power = extractTransmissionPower(pkt)

					channel = str(int(temp.info.encode("hex"), 16))
								
					print myTool.green + "[+] " + myTool.stop + str(currentDateAndTime) + ": Discovered Accesspoint (" + str(len(ssids)) + "):"
					print myTool.green + "[+] " + myTool.stop + "BSSID --> " + pkt.getlayer(Dot11).addr3
					print myTool.green + "[+] " + myTool.stop + "ESSID --> " + currSSID
					print myTool.green + "[+] " + myTool.stop + "channel --> " + channel
					print myTool.green + "[+] " + myTool.stop + "power --> " + power
			
					cap = pkt.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}\{Dot11ProbeResp:%Dot11ProbeResp.cap%}")
					if re.search("privacy", cap):
						encryption = "Yes"
					else:
						encryption = "No"
					print myTool.green + "[+] " + myTool.stop + "encryption --> " + encryption
					print ""
			
					statement = "insert into accesspoints (bssid, essid, channel, power, locationId, encryption, time) values (\"" + pkt.getlayer(Dot11).addr3 + "\", \"" + currSSID + "\", \"" + channel + "\", \"" + power + "\", \"" + str(locationID) + "\", \"" + encryption + "\", \"" + str(currentTimestamp) + "\")"
					connectionCursor.execute(statement)
					connection.commit()
			
					break
							
				# save SSID
				if temp.ID == 0:
					ssids.add(bssidEssidPair)
					currSSID = temp.info
					# save hidden ssids
					for byte in bytearray(currSSID):
						if byte == 0:
							currSSID = "[hidden]"
			
			temp = temp.payload

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
