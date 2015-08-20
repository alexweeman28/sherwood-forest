# sherwood-forest

This repository contains Python scripts and other files to support data exfiltration simulations in BetaPort.

* **startbot.py** -- Queries the men.xml file on the specified (and so far hard coded) Web server and sets up XMLRPC clients and/or servers, depending on the local host's sequence number in the bot chain. Each client within the chain will, every 30 seconds, relay whatever files appear in its data directory to the server downstream from it. Once these files have been transferred, they are removed from the local data directory.

* **csv2xml** -- This directory contains files that support the creation of human- and machine-readable XML files containing information on the software bots.

TO DO: 

* If the client can't communicate with a downstream server, in order by sequence number, it quits. This is a pain, because it requires all the bots to come up in order, from the sink backwards. Let's change this behavior. When a client is instantiated, let's take in on faith that the server will be there to receive files. If it happens that the server is down at this point, then let's work through the chain of servers at that point, by sequence number, to the sink. This could actually go on forever, as files pile up from upstream clients. But if we continue to run through this drill every 30 seconds, we'll have a more robust bot net. And that's what it's all about. But, as the Germans say, "Morgen is auch ein Tag."

* Thread the server--each response to a client connection should spawn a separate thread...how this is going to work with the lock, I'm not sure.
