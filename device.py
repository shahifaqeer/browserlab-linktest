#!/usr/bin/env python

from __future__ import division
#from datetime import datetime
#from random import randint
#from classes import Router, Client, Server
#from parsers import MyParser
#from collections import defaultdict

#import numpy as np
#import time
import socket
import paramiko
#import subprocess
#import shlex
#import struct
#import fcntl
#import sys
import traceback
#import logging

import const


CONTROL_PORT = const.CONTROL_PORT
RECV_BUFFER = 4096 #const.RECV_BUFFER

def debug(message):
    """print output to debug file AND screen using logging library"""
    #TODO
    print "DEBUG: " + message
    return

def master_slave(dev_name='A0', ipaddr='127.0.0.1', port=CONTROL_PORT):
    return Slave(dev_name, ipaddr, port, dev_type = 'A')

def wireless_slave(dev_name, ipaddr, port=CONTROL_PORT):
    return Slave(dev_name, ipaddr, port, dev_type = 'B')

def wired_slave(dev_name, ipaddr, port=CONTROL_PORT):
    return Slave(dev_name, ipaddr, port, dev_type = 'C')

def ip_addr_only(dev_name, ipaddr, port):
    return IPAddrOnly(dev_name, ipaddr, dev_type = 'D')

def router(dev_name='R0', ipaddr=const.ROUTER_ADDRESS_LOCAL, port=CONTROL_PORT):
    username=const.ROUTER_USER
    password=const.ROUTER_PASS
    return Router(dev_name, username, password, ipaddr, dev_type = 'R')

def server_slave(dev_name, ipaddr, port=CONTROL_PORT):
    return Slave(dev_name, ipaddr, port, dev_type = 'S')

get_device = {'A': master_slave,
              'B': wireless_slave,
              'C': wired_slave,
              'D': ip_addr_only,
              'R': router,
              'S': server_slave}


class Slave:
    def __init__(self, name, ipaddr, port, dev_type):
        self.name = name
        self.ip = ipaddr
        self.port = port
        self.devType = dev_type
        self.sock = None
        self.connect_socket()
        self.command({'CMD':'mkdir -p /tmp/browserlab/'})

    def connect_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
        except Exception, error:
            traceback.print_exc()
            debug("Can't connect to "+self.ip+":"+str(self.port)+". Check slave on "+self.name)
        return

    def command(self, msg):
        msg = str(msg)
        debug(self.name + ": " + msg)
        if self.sock is not None:
            self.sock.send(msg)
            #TODO do I need a sleep here?
            debug( "response " + self.sock.recv(RECV_BUFFER) )
        return


class Router:
    def __init__(self, name, user, passwd, ipaddr, dev_type):
        self.name = name
        self.ip = ipaddr
        self.user = user
        self.passwd = passwd
        self.devType = dev_type
        self.host = self.connectHost(ipaddr, user, passwd)
        self.blocking_cmd = 0
        self.remoteCommand('mkdir -p /tmp/browserlab/')

    def connectHost(self, ip, user, passwd):
        host = paramiko.SSHClient()
        host.load_system_host_keys()
        host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        debug('connect to ' + ip + ' user: ' + user + ' pass: ' + passwd)
        host.connect(ip, username=user, password=passwd)
        return host

    def remoteCommand(self, cmd):
        """This should be used for starting iperf servers, pings,
        tcpdumps, etc.
        """
        stdin, stdout, stderr = self.host.exec_command(cmd)
        if self.blocking_cmd:
            for line in stdout:
                debug(line)
        return

    def command(self, cmd):
        if 'BLK' in cmd:
            if cmd['BLK'] == 1:
                self.blocking_cmd = 1
        self.remoteCommand(cmd['CMD'])
        debug(self.name +": "+ str(cmd))
        return


class IPAddrOnly:
    def __init__(self, name, ipaddr, dev_type):
        self.name = name
        self.ip = ipaddr
        self.devType = dev_type

    def command(self, cmd):
        return


class Device:
    """expose name, ip, port, devType, command, and dev"""
    def __init__(self, dev_name, ipaddr, port, dev_type):
        self.name = dev_name
        self.ip = ipaddr
        self.port = port
        self.devType = dev_type
        #get device as Slave (master, wireless, wired, server), Router, or IPAddrOnly
        self.dev = get_device[dev_type](dev_name, ipaddr, port)
        #overload dev.command()
        self.command = self.dev.command

        #add device to self.devices{ dev_name: DEVICE CLASS }

    def check_alive(self):
        #TODO by pinging IP
        #TODO but maybe this is better as a higher level functionality
        return

