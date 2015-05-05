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


import os
from engineClasses.tools import tools


myTool = tools()


# set all import chmods
try:
        os.system("chmod +x run.py")
	print myTool.green + "[+] " + myTool.stop + "CHMOD(+x): run.py -> Success!"
except:
        print myTool.fail + "[-] " + myTool.stop + "CHMOD(+x): run.py -> FAIL!"
try:
        os.system("chmod +x scan.py")
        print myTool.green + "[+] " + myTool.stop + "CHMOD(+x): scan.py -> Success!"
except:
        print myTool.fail + "[-] " + myTool.stop + "CHMOD(+x): scan.py -> FAIL!"
try:
	os.system("chmod +x merge.py")
	print myTool.green + "[+] " + myTool.stop + "CHMOD(+x): merge.py -> Success!"
except:
	print myTool.fail + "[-] " + myTool.stop + "CHMOD(+x): merge.py -> FAIL!"
try:
	os.system("chmod +x cgi-bin/index.html")
	print myTool.green + "[+] " + myTool.stop + "CHMOD(+x): cgi-bin/index.html -> Success!"
except:
	print myTool.fail + "[-] " + myTool.stop + "CHMOD(+x): cgi-bin/index.html -> FAIL!"
try:
	os.system("chmod +x cgi-bin/control.html")
	print myTool.green + "[+] " + myTool.stop + "CHMOD(+x): cgi-bin/control.html -> Success!"
except:
	print myTool.fail + "[-] " + myTool.stop + "CHMOD(+x): cgi-bin/control.html -> FAIL!"
try:
	os.system("chmod +x cgi-bin/menu.html")
	print myTool.green + "[+] " + myTool.stop + "CHMOD(+x): cgi-bin/menu.html -> Success!"
except:
	print myTool.fail + "[-] " + myTool.stop + "CHMOD(+x): cgi-bin/menu.html -> FAIL!"
try:
	os.system("chmod +x cgi-bin/database.html")
	print myTool.green + "[+] " + myTool.stop + "CHMOD(+x): cgi-bin/database.html -> Success!"
except:
	print myTool.fail + "[-] " + myTool.stop + "CHMOD(+x): cgi-bin/database.html -> FAIL!"
try:
	os.system("chmod +x cgi-bin/largemap.html")
	print myTool.green + "[+] " + myTool.stop + "CHMOD(+x): cgi-bin/largemap.html -> Success!"
except:
	print myTool.fail + "[-] " + myTool.stop + "CHMOD(+x): cgi-bin/largemap.html -> FAIL!"

print myTool.green + "[+] " + myTool.stop + "All chmods set."
print ""

if not os.path.exists("data/merge"):
	os.makedirs("data/merge")
	print myTool.green + "[+] " + myTool.stop + "Folder data/merge created."
else:
	print myTool.warning + "[!] " + myTool.stop + "Folder data/merge already exists. Skipping..."