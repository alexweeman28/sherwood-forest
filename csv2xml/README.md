# sherwood-forest/csv2xml

The script and other files in this directory support the conversion of CSV files containing information on the sherwood-forest data exfiltration-bot network to machine- and human-readable XML files. It is envisioned that data on the bots will be maintained in a spreadsheet file, which will be exported to CSV format for conversion to XML. A sample CSV input file ```men.csv``` and XML output file ```men.xml``` produced by the included ```csv2xml.py``` script are included for reference.

## Files

**README.md:** This file.

**csv2xml.py:** This script imports a CSV file named ```men.csv``` from the current working directory and converts its contents to XML format, adding an one-up (auto-increment) integer id attribute, and writing a new file named ```men.xml``` to the current working directory. 

**men.csv:** This file contains information on the hosts that make up the data exfiltration network. The first line of this file should be a header, containing the column names: *ipaddress,port,seq_no,active*, representing each host's ip address, port number, sequence number and a True/False value indicating whether or not the node should be considered active. The ```csv2xml.py``` script imports this file and converts it to XML format. 

Regarding sequence numbers, the sequence number 0 is reserved for the very first host in the data exfiltration chain, and the number 99 is reserved for the very last bot in the chain. Intermediate hosts may be assigned any value in between. The relative sequence numbers determine the order in which files are passed from the source node (sequence number 0) to the sink node (sequence number 99).

**men.xml:** A sample XML file written by the ```csv2xml.py``` script after converting the data from ```men.csv``` to XML format.

**men.xsl:** An XML stylesheet to render a human-readable version of ```men.xml```when viewed in a Web browser. This stylesheet is referenced in the XML file and should be made available in the same directory on the Web server. 

## Installation

The ```csv2xml.py``` script uses only Python 3 standard libraries. No additional installation steps are required.

## Configuration and Use

Prior to running the ```csv2xml.py``` script, a CSV file named ```men.csv```, formatted as described above, should be placed in the current directory. After the script is run, the output file ```men.xml``` and the XSL stylesheet ```men.xsl``` should be placed on a Web server visible to all data exfiltration hosts.
