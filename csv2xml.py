#!/usr/bin/env python
# encoding: utf-8
"""
csv_to_xml.py

This script coverts a csv file to an XML.
The script takes 2 paramenters
  * csv filename, *with* header row
  * row node name; root node will be the plural
    version of the provided row node name

Created by Giovanni Collazo on 2011-02-19.
Copyright (c) 2011 24veces.com. All rights reserved.

Modified by Jim Owens on 2015-08-05.
  * Converted to Python 3 syntax
  * Created default values for input file and row node name
  * Made minor adjustments to output format
  
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import sys
import csv
from xml.dom.minidom import Document

def main(args):
  usage = "Usage: \n\t args[0] csv nodename\n\t csv: the name of a csv file (default: men.csv) WITH a header row, and\n\t nodename: tag for nodes" 
  try:
    filename = args[1]
    safe_filename = str.replace(filename[:-4], " ", "_").lower()
  except IndexError:
    try:
      filename = 'men.csv'
      safe_filename = 'men'
    except:
      print(usage)
      sys.exit()
    
  try:
    single_item = args[2]
  except IndexError:
    single_item = 'bot'
    #print(usage)
    #sys.exit()
  
  f = csv.reader(open(filename, 'r'))
  
  doc = Document()
  root_element = doc.createElement(safe_filename)
  doc.appendChild(root_element)

  pi = doc.createProcessingInstruction('xml-stylesheet',
                                       'type="text/xsl"'
                                       'href="men.xsl"')
  doc.insertBefore(pi, doc.firstChild)
  
  columns = next(f)
  
  for row in f:
    item = doc.createElement(single_item)
    root_element.appendChild(item)
    for c in enumerate(create_col_nodes(columns, item, doc)):
      # jpo: Strip white space from node entries
      row[0] = row[0].strip()
      c[1].appendChild(doc.createTextNode(row.pop(0)))
  
  output_file = safe_filename + ".xml"
  # jpo: Add indents and newlines to the XML output
  doc.writexml(open(output_file, 'w'), ' ' * 2, ' ' * 2, '\n') # Write file
  
  print("Done: Created %s" % output_file)
  
def create_col_nodes(cols, item, doc): 
  nodes = []
  for col in cols:
    node = doc.createElement(str.replace(col, " ", "_").lower())
    item.appendChild(node)
    nodes.append(node)
  
  return nodes

if __name__ == "__main__":
  sys.exit(main(sys.argv))
