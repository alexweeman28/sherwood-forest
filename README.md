# sherwood-forest

This repository contains Python scripts and other files to support data exfiltration simulations in BetaPort.

* **startbot.py** -- Queries the men.xml file on the specified (so far hard coded) Web server and sets up XMLRPC clients and/or servers, depending on the local host's sequence number in the bot chain.

* **csv2xml** -- This directory contains files that support the creation of human- and machine-readable XML files containing information on the software bots.

TO DO: 

* On server start, need to check that a server instance isn't already running...
