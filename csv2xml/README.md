# sherwood-forest
## csv2xml files

The files in this directory support the conversion of CSV files containing information on sherwood-forest bots to machine- and human-readable XML files. The files are:

* csv2xml.py
* men.csv
* men.xml
* men.xsl

It is envisioned that data on the bots will be maintained in a spreadsheet file, which will be exported to CSV format for conversion to XML.

The included **csv2xml.py** script assumes that a CSV file named men.csv is available in the current working directory. The first line of this file should be a header, containing the column names: ipaddress,port,active. The script imports this file and converts it to XML format, adding an one-up integer id attribute. The XML file is written to the current working directory.

An XML stylesheet, **men.xsl**, is also included to produce a human-readable version of the XML file when viewed in a Web browser. This stylesheet is referenced in the XML file produced by csv2xml and should be available in the current working directory.

A sample CSV input file **men.csv** and XML output file **men.xml** produced by the script are also included for reference.
