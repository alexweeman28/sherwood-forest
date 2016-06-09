# sherwood-forest

Python scripts and other files to support data exfiltration simulations in BetaPort.

## Files

**startbot.py:** Queries the men.xml file on the specified (and so far hard coded) Web server and sets up XMLRPC clients and/or servers, depending on the local host's sequence number in the bot chain. Each client within the chain will, every 30 (configurable) seconds, relay whatever files appear in its data directory to the server immediately downstream from it, by sequence number. Once files have been transferred, they are removed from the client's local data directory. If the server immediately downstream cannot be contacted, then the client attempts to contact each successive server in the chain, by sequence number, until it either finds a server to send the files to or runs out of servers to try. If a file transfer fails because no server could be contacted, the client simply waits until the next sending opportunity to try it all over again. At node 0 only, the script also builds a wishlist of files to steal, which is stored in a local SQLite3 table in priority order. Then one file is transferred to the data directory during each iteration of the infinite loop, from which it is subsequently exfiltrated to the downstream server.

**csv2xml:** This directory contains files that support the creation of human- and machine-readable XML files containing information on the software bots. See ```csv2xml/README.md``` for details.

## Installation

## Configuration and Use
