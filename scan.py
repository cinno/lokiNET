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
import md5


myTool = tools()
clientProbes = set()
currentTimestamp = time.time()
currentDateAndTime = datetime.datetime.fromtimestamp(currentTimestamp).strftime("%Y-%m-%d %H:%M:%S")
interface = sys.argv[1]
signature = sys.argv[2]
privacy = int(sys.argv[4])
silent = int(sys.argv[5])
dataFile = signature + "Data.db"
locationID = int(sys.argv[3])
ssids = set()
clientAPSet = set()
path = os.path.split(os.path.realpath(__file__))[0]


def dbSelectCommit(statement):
	connectionCursor.execute(statement)
	return connectionCursor.fetchall()

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
		if silent == 0:
			print myTool.warning + "[!] " + myTool.stop + "Extracting transmission power failed..."

        return power


def pktHandler(pkt):
	# scan for datapackets
	if pkt.haslayer(Dot11):
		curPkt = pkt.getlayer(Dot11)
		if curPkt.type == 2:
			if curPkt.addr1 != "ff:ff:ff:ff:ff:ff" and curPkt.addr2 != "ff:ff:ff:ff:ff:ff" and curPkt.addr2 != "00:00:00:00:00:00" and curPkt.addr1 != "00:00:00:00:00:00":
				address1 = curPkt.addr1
				address2 = curPkt.addr2

				if privacy == 1:
					address1 = md5.new(signature + address1).hexdigest()
			                address2 = md5.new(signature + address2).hexdigest()

				comb1 = address1 + " " + address2
				comb2 = address2 + " " + address1

				# look if combination is already in database
				combInDB = 0
				combInDatabase = dbSelectCommit("select ID from connections where macOne=\"" + address1 + "\" and macTwo=\"" + address2 + "\"")
				if len(combInDatabase) != 0:
					combInDB = 1
				combInDatabase = dbSelectCommit("select ID from connections where macOne=\"" + address2 + "\" and macTwo=\"" + address1 + "\"")
				if len(combInDatabase) != 0:
					combInDB = 1
				if comb1 not in clientAPSet and comb2 not in clientAPSet and combInDB == 0:
					clientAPSet.add(comb1)
					clientAPSet.add(comb2)

					# extract transmission power
					power = extractTransmissionPower(pkt)
					if silent == 0:
						print myTool.green + "[+] " + myTool.stop + str(currentDateAndTime) + ": Data exchange between " + address1 + " and " + address2 + " (" + str(int(len(clientAPSet)/2)) + "):"
						print myTool.green + "[+] " + myTool.stop + "power --> " + power
						print ""

					# save tupel data to database
					dbChangeCommit("insert into connections (macOne, macTwo, power, locationId, timeFirst, timeLast) values (\"" + address1 + "\", \"" + address2 + "\", \"" + power + "\", \"" + str(locationID) + "\", \"" + str(currentTimestamp) + "\", \"" + str(currentTimestamp) +  "\")")
				else:
					dbChangeCommit("UPDATE connections SET timeLast='" + str(currentTimestamp) + "' WHERE macOne='" + address1 + "' AND macTwo='" + address2 + "'")
					dbChangeCommit("UPDATE connections SET timeLast='" + str(currentTimestamp) + "' WHERE macOne='" + address2 + "' AND macTwo='" + address1 + "'")

	# scan for probe requests
	if pkt.haslayer(Dot11ProbeReq):
		curSSID = "[broadcast]"
 		if len(pkt.getlayer(Dot11ProbeReq).info) > 0:
			curSSID = pkt.getlayer(Dot11ProbeReq).info
		clientMac = pkt.getlayer(Dot11).addr2

		if privacy == 1:
			clientMac = md5.new(signature + str(clientMac)).hexdigest()
			if curSSID != "[broadcast]":
				curSSID = md5.new(signature + curSSID).hexdigest()
	        newCombination = clientMac + " " + curSSID
		# look if combination is already in database
		combInDatabase = dbSelectCommit("select ID from clientProbes where clientMac=\"" + clientMac + "\" and probe=\"" + curSSID + "\"")
		if newCombination not in clientProbes and len(combInDatabase) == 0:
			clientProbes.add(newCombination)

			# extract transmission power
			power = extractTransmissionPower(pkt)

			if silent == 0:
				print myTool.green + "[+] " + myTool.stop + str(currentDateAndTime) + ": Discovered new unique probe request (" + str(len(clientProbes)) + "): "
			if privacy == 0:
				if silent == 0:
					print myTool.green + "[+] " + myTool.stop + "MAC --> " +  clientMac
					print myTool.green + "[+] " + myTool.stop + "probe --> " + curSSID
			else:
				if silent == 0:
					print myTool.green + "[+] " + myTool.stop + "scrambled MAC --> " +  clientMac
					print myTool.green + "[+] " + myTool.stop + "probe --> " + curSSID
			if silent == 0:
				print myTool.green + "[+] " + myTool.stop + "power --> " + power
				print ""

			# save tupel to database
			dbChangeCommit("insert into clientProbes (clientMac, probe, locationId, power, timeFirst, timeLast) values (\"" + clientMac + "\", \"" + curSSID + "\", \"" + str(locationID) + "\", \"" + power + "\", \"" + str(currentTimestamp) + "\", \"" + str(currentTimestamp) + "\")")
		else:
			# update last seen parameter
			dbChangeCommit("UPDATE clientProbes SET timeLast='" + str(currentTimestamp) + "' WHERE clientMac='" + clientMac + "' AND probe='" + curSSID + "'")

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

					if silent == 0:
						print myTool.green + "[+] " + myTool.stop + str(currentDateAndTime) + ": Discovered Accesspoint (" + str(len(ssids)) + "):"
					if privacy == 0:
						bssid = pkt.getlayer(Dot11).addr3
						if silent == 0:
							print myTool.green + "[+] " + myTool.stop + "BSSID --> " + bssid
							print myTool.green + "[+] " + myTool.stop + "ESSID --> " + currSSID
					else:
						bssid = md5.new(signature + str(pkt.getlayer(Dot11).addr3)).hexdigest()
						if silent == 0:
							print myTool.green + "[+] " + myTool.stop + "scrambled BSSID --> " + bssid
						if currSSID != "[hidden]":
							currSSID = md5.new(signature + currSSID).hexdigest()
						if silent == 0:
							print myTool.green + "[+] " + myTool.stop + "scrambled ESSID --> " + currSSID
					if silent == 0:
						print myTool.green + "[+] " + myTool.stop + "channel --> " + channel
						print myTool.green + "[+] " + myTool.stop + "power --> " + power

					cap = pkt.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}\{Dot11ProbeResp:%Dot11ProbeResp.cap%}")
					if re.search("privacy", cap):
						encryption = "Yes"
					else:
						encryption = "No"
					if silent == 0:
						print myTool.green + "[+] " + myTool.stop + "encryption --> " + encryption
						print ""

					dbChangeCommit("insert into accesspoints (bssid, essid, channel, power, locationId, encryption, time) values (\"" + bssid + "\", \"" + currSSID + "\", \"" + channel + "\", \"" + power + "\", \"" + str(locationID) + "\", \"" + encryption + "\", \"" + str(currentTimestamp) + "\")")

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
connection = sqlite3.connect(path + "/data/" + dataFile)
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
