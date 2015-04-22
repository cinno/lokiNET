#!/usr/bin/python


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

print myTool.green + "[+] " + myTool.stop + "All chmods set."
