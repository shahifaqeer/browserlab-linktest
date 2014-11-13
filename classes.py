#!/usr/bin/env python

from __future__ import division

import const
import time
import socket
import os
import paramiko
import threading
import subprocess
#import shlex
import sys
import traceback


def logcmd(cmd, name):
    if not os.path.exists('/tmp/browserlab/'):
        os.mkdir('/tmp/browserlab/')
    fileout = open('/tmp/browserlab/A_logcmd.log', 'a+w')
    fileout.write(name + ': ' + str(time.time()) + ': ' + cmd + '\n')
    print 'DEBUG: ' + name + ': ' + str(time.time()) + ': ' + cmd
    fileout.close()
    return


# client commands
class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        print self.process.returncode


class Router:
    def __init__(self, ip, user, passwd, name='R'):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.name = 'R'
        self.host = self.connectHost(ip, user, passwd)
        self.blocking_cmd = 0
        self.remoteCommand('mkdir -p /tmp/browserlab/')

    def connectHost(self, ip, user, passwd):
        host = paramiko.SSHClient()
        host.load_system_host_keys()
        host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print 'DEBUG: connect to ' + ip + ' user: ' + user + ' pass: ' + passwd
        host.connect(ip, username=user, password=passwd)
        return host

    def remoteCommand(self, cmd, block=0):
        """This should be used for starting iperf servers, pings,
        tcpdumps, etc.
        """
        stdin, stdout, stderr = self.host.exec_command(cmd)
        if block:
            for line in stdout:
                print 'DEBUG: '+ line
        return

    def command(self, cmd):
        block = 0
        if 'BLK' in cmd:
            if cmd['BLK'] == 1:
                block = cmd['BLK']
        self.remoteCommand(cmd['CMD'], block)
        logcmd(str(cmd), self.name)
        return


class Client:
    def __init__(self, ip, name='A'):
        self.name = name
        self.ip = ip
        #self.logfile = initialize_logfile()

    def command(self, cmd):
        logcmd(str(cmd), self.name)
        if not ('TIMEOUT' in cmd):
            if 'STDOUT' in cmd:
                outfile = open(cmd['STDOUT'], 'a+w')
            else:
                outfile = None
            #use subprocess for immediate command
            p = subprocess.call(cmd['CMD'], stdout=outfile, shell=True)
        else:
            Command(cmd['CMD']).run(cmd['TIMEOUT'])
        return


class Server:
    def __init__(self, ip, port=const.CONTROL_PORT, name='S'):
        self.name = name
        self.ip = ip
        self.port = port
        #self.logfile = initialize_logfile()

    def command(self, cmd):
        if type(cmd) is dict:
            msg = str(cmd)  # remember to eval and check for flags on other end (START, TIMEOUT, CMD, SUDO(?))

        num_retries = 0
        while num_retries<10:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.ip, self.port))
                s.send(msg)
                response = s.recv(const.MSG_SIZE)
                print 'RECEIVED ', response
                res = response
                #res, run_num, pid = response.split(',')
                while res == 1 or res == '1':
                    print 'Server is busy. Try again later.'
                s.close()
                if num_retries > 0:
                    run_num = "x"+run_num
                    msg = 'SCREWED ' + msg
                logcmd(msg, self.name)
                return res#, run_num, pid
            except Exception, error:
                print "DEBUG: Can't connect to "+str(self.ip)+":"+str(self.port)+". This measurement is screwed "+ str(error) +". \nRETRY "+str(num_retries+1)+" in 2 seconds."
                traceback.print_exc()
                num_retries += 1
                time.sleep(2)
                continue
            break
        raw_input("Server unresponsive. Press any key to exit. ")
        sys.exit()
        return

    def __del__(self):
        print "Close connection to server"


