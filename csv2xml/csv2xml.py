#!/usr/bin/env python
"""
csv2xml.py

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
  # Input file should be called men.csv
  filename = 'men.csv'
  # The XML nodes will be named <bot>
  single_item = 'bot'
  safe_filename = filename[:-4]
  
  try:
    f = csv.reader(open(filename, 'r'))
  except IOError:
    print('ERROR: Input file men.csv not found in current working directory')
    sys.exit()
    
  doc = Document()
  # Use the file name as the root node name
  root_element = doc.createElement(safe_filename)
  doc.appendChild(root_element)
  # Add the style sheet info
  pi = doc.createProcessingInstruction('xml-stylesheet',
                                       'type="text/xsl"'
                                       'href="men.xsl"')
  doc.insertBefore(pi, doc.firstChild)
  # Get the header row from the csv file
  # If it's missing or short, use a default
  columns = next(f)
  if len(columns) < 4:
    columns = ['ipaddress','port','seq_no','active']

  # Remove white space from around column names
  for i in range(len(columns)):
    columns[i] = columns[i].strip()

  # Populate the XML document
  index = 0
  for row in f:
    index += 1
    item = doc.createElement(single_item)
    item.setAttribute('id', str(index))
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
