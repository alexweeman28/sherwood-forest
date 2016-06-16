# sherwood-forest

Python scripts and other files to support data exfiltration simulations in BetaPort.

## Files

**startbot.py:** This Python 3 script queries the men.xml file on the specified Web server and sets up a number of XMLRPC clients and/or servers, depending on the local host's sequence number in the bot chain. Each client within the chain will, every 30 (configurable) seconds, relay whatever files appear in its data directory to the server immediately downstream from it, by sequence number. Once files have been transferred, they are removed from the client's local data directory. If the server immediately downstream cannot be contacted, then the client attempts to contact each successive server in the chain, by sequence number, until it either finds a server to send the files to or runs out of servers to try. If a file transfer fails because no server could be contacted, the client simply waits until the next sending opportunity to try it all over again. At node 0 (the first bot in the chain) only, the script also builds a wishlist of files to steal, which is stored in a local SQLite3 table in priority order. Then one file is transferred to the data directory during each iteration of an infinite loop, from which it is subsequently exfiltrated to the downstream server.

**csv2xml:** This directory contains files that support the creation of human- and machine-readable XML files containing information on the software bots. See ```csv2xml/README.md``` for details.

## Installation
The ```startbot.py``` script uses only Python 3 standard libraries. No additional installation steps are required. It should be noted, however, that this script uses the sqlite3 module in the Python Standard Library to create, populate and query an SQLite3 database. It may therefore be useful to install Ubuntu's sqlite3 package to provide a command line interface to the database:
```
sudo apt-get install sqlite3
```

## Configuration and Use
