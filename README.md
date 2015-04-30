<h1>lokiNET</h1>
<i>Version 1.5.13 - Release: Dagger</i>
<hr>
<h2>About:</h2>
Location-based service which observes and stores all the different wireless devices and their properties around. Should be used at different locations simultaneously to be effective<br>
The application consists of two different parts: scanengine and webinterface.
This application is part of my master thesis.
<ul>
<li>scanengine: Scans for all wireless devices around and stores them into a database.</li>
<li>webinterface: Can be used to analyze collected data.</li>
<li>You can run the program using the run-script. To list all available commands use the "-h" option. If you run the program in offline mode it will not try to translate a address into GPS coordinates (It can be translated afterwards using the webinterface).</li>
</ul>
<hr>
<h2>Scenario:</h2>
An attacker may create some small linux devices where this software is installed and configured. Then he places the devices at different locations and let them do their "work". After a while he collect the devices, migrates all database files to one and analyze the data. Then he is able to reconstruct wifi client movements and behaviour.
<hr>
<h2>Requirements:</h2>
<ul>
<li>Linux system</li>
<li>Python 2.7</li>
<li>Scapy</li>
<li>sqlite3 module for python</li>
</ul>
<hr>
<h2>Installation:</h2>
<ul>
<li>Before you first run the program you should execute the setup script (python setup.py)</li>
<li>IMPORTANT: If you run this script under root user, you have to edit CGIHTTPServer.py file: Just search for <i>os.setuid(nobody)</i> and overwrite it with <i>os.setuid(0)</i></li>
</ul>
<h2>Usage Examples:</h2>
<ul>
<li>HINT: You always have to use your wifi card in monitor mode! (use airmon-ng or the built in -m option of this tool)</li>
<li>Start the scanengine in offline mode and using the address format: ./run [wireless_interface]</li>
<li>Start the scanengine in offline mode and using the address format while privacy protection is activated: ./run [wireless_interface] -p</li>
<li>Start the webinterface: ./run.py -web</li>
</ul>
<hr>
<h2>Privacy Mode</h2>
<p>The privacy option takes care that every sniffed MAC address, ESSID and probe gets scrambled before it gets stored inside the database. The user input "signature" works as encryption key in the scrambling process. You can activate privacy by using the -p/--privacy option.</p>
<hr>
<h2>License:</h2>
<p>Copyright 2015 Daniel Haake</p>
<p>This program is free software: you can redistribute it and/or modify<br />
it under the terms of the GNU General Public License as published by<br />
the Free Software Foundation, either version 3 of the License, or<br />
(at your option) any later version.</p>
<p>This program is distributed in the hope that it will be useful,<br />
but WITHOUT ANY WARRANTY; without even the implied warranty of<br />
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the<br />
GNU General Public License for more details.<br /></p>
<p>You should have received a copy of the GNU General Public License<br />
along with this program.  If not, see <http://www.gnu.org/licenses/>.</p>
