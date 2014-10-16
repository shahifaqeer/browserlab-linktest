#!/usr/bin/env python

#SERVER
from __future__ import division
#from datetime import datetime
import socket
#import random
import subprocess
import threading
import os
import time
import traceback
#import json
#import const

SERVER_NAME = 'S'
port = raw_input("Enter CONTROL PORT [DEFAULT = 12345]: ")
if port == "":
    port = 12345
else:
    port = int(port)
password = raw_input("Enter password for sudo access *not compulsary* (cleartext): ")
port_max = port+5
backlog = 5
size = 1024
run_number = 100000
experiment_timeout = 10
transfer_timeout = experiment_timeout + 2
global BUSY


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        if not (os.path.exists('/tmp/browserlab/')):
            os.mkdir('/tmp/browserlab/')
        self.fout = open('/tmp/browserlab/'+SERVER_NAME+'_debug.log', 'a+w')

    def run(self, timeout):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        self.debug()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        print self.process.returncode

    def debug(self):
        now = time.time()
        print str(now) +': '+ self.cmd
        self.fout.write(str(now) + ': ' + self.cmd + '\n')


def clientthread(conn):
    conn.send("Type command\n")

    while True:
        data = conn.recv(size)
        reply = 'OK...' + data
        if not data:
            break
        else:
            ret_code = execute_command(data)
            reply = str(ret_code)
        conn.sendall(reply)
    conn.close()
    return

def execute_command(data):

    if not (os.path.exists('/tmp/browserlab/')):
        os.mkdir('/tmp/browserlab/')

    try:
        msg = eval(data)
        #msg = json.loads(data)
    except Exception:
        traceback.print_exc()
        return -1

    if 'START' in msg:
        run_time = time.time()
        return run_time

    if 'CMD' in msg:
        print 'DEBUG: Started command: ' + msg['CMD'] + ' at time: '+str(time.time())+'\n'
        if 'SUDO' in msg:
            if msg['SUDO'] == 1:
                msg['CMD'] = 'echo "'+password+'" | sudo -S ' + msg['CMD']
        if 'TIMEOUT' in msg:
            pid = Command(msg['CMD']).run(msg['TIMEOUT'])
        else:
            if 'STDOUT' in msg:
                outfile = msg['STDOUT']
            else:
                outfile = None
            pid = subprocess.call(msg['CMD'], stdout=outfile, stderr=subprocess.STDOUT, shell=True)
            #out = subprocess.check_output(msg['CMD'], stdout=outfile, shell=True)
        print 'DEBUG: Finished command: ' + msg['CMD'] + ' at time: '+str(time.time())+'; PID = '+str(pid)+'\n'
        return 0
    else:
        print 'PROBLEM: no CMD in msg'
        return -1


if __name__ == "__main__":

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while (port<port_max):
        #try ports 12345 to 12349
        try:
            s.bind(('', port))
            print "Open server at port " + str(port)
            break;
        except Exception:
            port += 1
            traceback.print_exc()

    s.listen(backlog)
    global BUSY
    BUSY = 0


    while 1:
        conn, address = s.accept()
        print "Connected with ", address
        #start_new_thread( clientthread, (conn,))
        clientthread(conn)
        #data = client.recv(size)
        #if data:
        #    ret_code = execute_command(data)
        #    client.send(str(ret_code))

    s.close()
