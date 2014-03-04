#SERVER
from __future__ import division
from datetime import datetime
import socket
import random
import subprocess
import threading
import os
import time

CLIENT_ADDRESS = 'localhost'
SERVER_ADDRESS = '130.207.97.240'
ROUTER_ADDRESS = '50.167.212.31'
port = 12345
backlog = 5
size = 1024
run_number = 100000
experiment_timeout = 10
transfer_timeout = experiment_timeout + 2
global BUSY

'''
class SwitchFlag(threading.Thread):
    def run(self):
        print 'B = 1'
        BUSY = 1
        time.sleep(experiment_timeout + 5)
        print 'B = 0'
        BUSY = 0
'''


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        if not (os.path.exists('/tmp/browserlab/')):
            os.mkdir('/tmp/browserlab/')
        self.fout = open('/tmp/browserlab/S_debug.log', 'a+w')

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

#def tcpdump():
#    return subprocess.call('tcpdump -i any -w /tmp/browserlab/S.pcap -G 10 &', shell=True)

#def fping():
#    return subprocess.call('tcpdump -i any -w /tmp/browserlab/S.pcap -G 10 &', shell=True)

def execute_command(msg):

    if not (os.path.exists('/tmp/browserlab/')):
        os.mkdir('/tmp/browserlab/')

    #if msg == 'tcpdump':
    #    return tcpdump()

    if 'CMD' in msg:
        print 'DEBUG: Started command: ' + msg['CMD'] + '\n'
        #if 'SUDO' in msg:
        #    if msg['SUDO'] == 1:
        #        msg['CMD'] = 'echo "hattorihanzo" | sudo -S ' + msg['CMD']
        if 'TIMEOUT' in msg:
            pid = Command(msg['CMD']).run(msg['TIMEOUT'])
        else:
            if 'STDOUT' in msg:
                outfile = msg['STDOUT']
            else:
                outfile = None
            pid = subprocess.call(msg['CMD'], stdout=outfile, shell=True)
        print 'DEBUG: Finished command: ' + msg['CMD'] + '\n'
        return 0
    else:
        print 'PROBLEM: no CMD in msg'
        return -1


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', port))
s.listen(backlog)
global BUSY
BUSY = 0

while 1:
    client, address = s.accept()
    print "Connection by ", address
    data = client.recv(size)
    if data:
        print data
        #print 'BUSY = ', BUSY
        BUSY = 0
        msg = eval(data)
        if 'START' in msg:
            #instead of run number lets use time.time()
            run_number = time.time()
        client.send(str(BUSY)+','+str(run_number)+','+str(0))
        print 'execute command ', msg
        pid = execute_command(msg)
