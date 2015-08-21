# sherwood-forest

This repository contains Python scripts and other files to support data exfiltration simulations in BetaPort.

* **startbot.py** -- Queries the men.xml file on the specified (and so far hard coded) Web server and sets up XMLRPC clients and/or servers, depending on the local host's sequence number in the bot chain. Each client within the chain will, every 30 (configurable) seconds, relay whatever files appear in its data directory to the server downstream from it. Once these files have been transferred, they are removed from the local data directory. If the server immediately downstream cannot be contacted, then the client attempts each successive server in the chain, by sequence number, until it finds a server to send the files to or runs out of servers to try. If transfer fails because no server could be contacted, the client simply waits until the next sending opportunity to try it all over again.

* **csv2xml** -- This directory contains files that support the creation of human- and machine-readable XML files containing information on the software bots.

TO DO: 

* Thread the server? Should each response to a client connection spawn a separate thread? How this is going to work with the lock, I'm not sure...
