# sherwood-forest

Python scripts and other files to support data exfiltration simulations in BetaPort.

## Files

**csv2xml/:** This directory contains files that support the creation of human- and machine-readable XML files containing information on the software bots. See ```csv2xml/README.md``` for details.

**README.md:** This file.

**settings.ini:** Sample configuration file containing default settings to control the behavior of the StartBots.

**startbot.py:** This Python 3 script queries the men.xml file on the specified Web server and sets up a number of XMLRPC clients and/or servers, depending on the local host's sequence number in the bot chain. Each client within the chain will, every 30 (configurable) seconds, relay whatever files appear in its data directory to the server immediately downstream from it, by sequence number. Once files have been transferred, they are removed from the client's local data directory. If the server immediately downstream cannot be contacted, then the client attempts to contact each successive server in the chain, by sequence number, until it either finds a server to send the files to or runs out of servers to try. If a file transfer fails because no server could be contacted, the client simply waits until the next sending opportunity to try it all over again. At node 0 (the first bot in the chain) only, the script also builds a wishlist of files to steal, which is stored in a local SQLite3 table in priority order. Then one file is transferred to the data directory during each iteration of an infinite loop, from which it is subsequently exfiltrated to the downstream server.

## Installation
The ```startbot.py``` script uses only Python 3 standard libraries. No additional installation steps are required. It should be noted, however, that this script uses the sqlite3 module in the Python Standard Library to create, populate and query an SQLite3 database. It may therefore be useful to install Ubuntu's sqlite3 package to provide a command line interface to the database:
```
sudo apt-get install sqlite3
```

## Configuration and Use
Configuration begins with the creation of a CSV (comma-separated values) file named ```men.csv``` containing a list of the hosts that make up the data exfiltration network. The entries in this file should include for each host the IP address, a port number to be used for a local XMLRPC server, a sequence number in the data exfil network, and a Boolean value indicating whether or not the host is considered active. A sample ```men.csv``` file can be found in the ```csv2xml/``` directory, along with instructions for converting its data to XML format. See ```csv2xml/README.md``` for details.

Once the data in ```men.csv``` has been converted to XML format and stored in ```men.xml```, this file along with ```men.xslt``` (included in ```csv2xml/```) should be placed on a Web server that is accessible via the network to all data exfiltration hosts.

When the ```startbot.py``` script is run, the data exfiltration hosts identified in ```men.xml``` will essentially form a bucket brigade, the purpose of which will be to steal files from a source node (the node specified in ```men.xml``` with sequence number 0, and forward them through the series of participating hosts, based on their sequence numbers, until the host with sequence number 99 is reached. This "sink" node serves as the final destination for stolen files. The list of files and directories to be stolen from the source node are specified in the ```settings.ini``` file, along with other configuration settings. See the sample file included in this repository for the default settings.

To initiate data exfiltration, simply copy the files in this repository to each participating host identified in the ```men.xml``` file, adjust the configuration in ```settings.ini``` as desired, and start the script on each host as shown below:
```
python3 startbot.py
```
The script can be halted by pressing Ctrl-c at each participating host.
