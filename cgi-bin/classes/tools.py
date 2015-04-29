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

import urllib2
import sqlite3
from xml.dom.minidom import parseString


class tools:
	def streetToGps(self, urlString):
		url = urllib2.urlopen(urlString)
		data = url.read()
		url.close()
		dom = parseString(data)
		xmlData = dom.getElementsByTagName("lat")[0].toxml()
		lat = xmlData.replace("<lat>", "")
		lat = lat.replace("</lat>", "")
		xmlData = dom.getElementsByTagName("lng")[0].toxml()
		lng = xmlData.replace("<lng>", "")
		lng = lng.replace("</lng>", "")
		result = [lat, lng]
		return result

	def connectToDatabase(self):
		dataFile = self.getSignature()
		connection = sqlite3.connect("data/" + dataFile)
		return connection.cursor()
	
	def dbSelect(self, connectionCursor, statement):
		connectionCursor.execute(statement)
		return connectionCursor.fetchall()	

	def getSignature(self):
		f = open('webfiles/config')
		dataFile = f.readlines()[0] + "Data.db"
		f.close()
		return dataFile