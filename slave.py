#!/usr/bin/env python

#SERVER
from __future__ import division
#from datetime import datetime
import socket
import select
import fcntl
import struct
#import random
import subprocess
import threading
import os
import time
import traceback
#import json
#import const
import logging

SERVER_NAME = 'S'
PORT = 12345
PORT_MAX = 12355
backlog = 10
RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
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

    def run(self, timeout=10):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, stderr=subprocess.STDOUT, shell=True)
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


def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                            ifname[:15]))[20:24])

def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
            ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip

def clientthread(conn):
    #conn.send("Type command\n")
    while True:
        data = conn.recv(size)
        reply = 'OK...' + data
        if not data:
            break
        else:
            ret_code = execute_command(data)
            reply = str(ret_code)
            print 'DEBUG: reply to send is: ' + reply
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
        print 'DEBUG: START run time: ' + str(run_time) + ' at time: '+str(time.time())
        return run_time

    if 'MASTER' in msg:
        master_ip = msg['MASTER']
        slave_ip = get_lan_ip()
        print 'DEBUG: MASTER IP: ' + master_ip + '; SLAVE IP: ' + slave_ip + ' at time: '+str(time.time())
        return slave_ip

    if 'CMD' in msg:
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
        print 'DEBUG: Finished command: ' + msg['CMD'] + ' at time: '+str(time.time())
        return 0
    else:
        print 'PROBLEM: no CMD in msg'
        return -1

def select_socket_server(PORT, password):
    CONNECTION_LIST = []    # list of socket clients

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    while (PORT<PORT_MAX):
        #try ports 12345 to 12349
        try:
            server_socket.bind(("", PORT))
            print "Open server at port " + str(PORT)
            break;
        except Exception:
            PORT += 1
            traceback.print_exc()

    server_socket.listen(backlog)

    CONNECTION_LIST.append(server_socket)

    while 1:
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

        for sock in read_sockets:
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        ret_code = execute_command(data)
                        reply = str(ret_code)
                        sock.send(reply)
                # client disconnected, so remove from socket list
                except:
                    #broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
    server_socket.close()
    return

def thread_socket_server(PORT, password):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while (PORT<PORT_MAX):
        #try ports 12345 to 12349
        try:
            s.bind(('', PORT))
            print "Open server at port " + str(PORT)
            break;
        except Exception:
            PORT += 1
            traceback.print_exc()

    s.listen(backlog)

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
    return

def simple_sender(PORT=12345):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', PORT))
    while 1:
        msg = raw_input('type test msg as dict format {"CMD":"abc"}: ')
        s.send(str(msg))
        #time.sleep(1)
        print s.recv(RECV_BUFFER)
    return
#def get_ip_address():
#    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#    ipaddr = socket.inet_ntoa(fcntl.ioctl(
#            s.fileno(),
#            0x8915,  # SIOCGIFADDR
#            struct.pack('256s', ifname[:15])
#        )[20:24])
#    return ipaddr
#
#
#def get_default_interface():
#    iface = []
#    route = subprocess.check_output('cat /proc/net/route', shell=True).split('\n')
#    for interface in route:
#        if interface != '':
#            x = interface.split('\t')
#            if x[3] == '0003' and x[2] != '00000000':
#                iface.append(x[0])
#    if len(iface) == 1:
#        return iface[0]
#    else:
#        return 'wlan0'      #DEFAULT INTERFACE NAME

if __name__ == "__main__":
    port = raw_input("Enter CONTROL PORT [DEFAULT = 12345]: ")
    if port == "":
        PORT = 12345
    else:
        PORT = int(port)
    password = raw_input("Enter password for sudo access *not compulsary* (cleartext): ")

    thread_socket_server(PORT, password)
