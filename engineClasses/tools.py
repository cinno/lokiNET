#!/usr/bin/python


import urllib2
from xml.dom.minidom import parseString


class tools:
	blue = "\033[94m"
	green = "\033[92m"
	warning = "\033[93m"
	fail = "\033[91m"
	stop = "\033[0m"

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