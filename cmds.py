#!/usr/bin/env python

from __future__ import division
#from datetime import datetime
#from random import randint

import time
import socket
import os
import paramiko
import threading
import subprocess
#import shlex
import struct
import fcntl

from const import *


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
    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.name = 'R'
        #self.logfile = initialize_logfile()
        self.server = SERVER_ADDRESS
        self.client = CLIENT_ADDRESS
        self.router = ROUTER_ADDRESS_LOCAL
        self.host = self.connectHost(ip, user, passwd)
        self.remoteCommand('mkdir -p /tmp/browserlab/')
        #self.initialize_servers()

    def connectHost(self, ip, user, passwd):
        host = paramiko.SSHClient()
        host.load_system_host_keys()
        host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print 'DEBUG: connect to ' + ip + ' user: ' + user + ' pass: ' + passwd
        host.connect(ip, username=user, password=passwd)
        return host

    def remoteCommand(self, cmd):
        """This should be used for starting iperf servers, pings,
        tcpdumps, etc.
        """
        stdin, stdout, stderr = self.host.exec_command(cmd)
        #for line in stdout:
        #    print 'DEBUG: '+ line
        return

    def command(self, cmd):
        self.remoteCommand(cmd['CMD'])
        logcmd(str(cmd), self.name)
        return

    """
    def initialize_servers(self):
        # iperf tcp serverip
        self.remoteCommand('iperf -s >> ' + self.name + '_iperf_tcp_server.log &')
        # iperf udp server
        self.remoteCommand('iperf -s -u >> '+ self.name + '_iperf_udp_server.log &')
        # udp probe server
        self.remoteCommand('udpprobeserver >> ' + self.name + '_udpprobe_server.log &')
        return 0
    """


class Client:
    def __init__(self, ip):
        self.name = 'A'
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

    """
    def fping(self, list_of_IPs=None):
        if list_of_IPs is None:
            y = ROUTER_ADDRESS_LOCAL+' '+ SERVER_ADDRESS
        else:
            y = ''
            for x in list_of_IPs:
                y = y + x + ' '
        self.command({'CMD':'fping '+ y +' -p 100 -c '+ str(experiment_timeout * 10) + ' -r 1 -A >> /tmp/browserlab/fping_A.log',
                   'TIMEOUT': experiment_timeout})
        return

    def tcpdump(self):
        return

    def radiotapdump(self):
        return

    def iperf_tcp_server(self):
        return

    def iperf_tcp_client(self):
        return

    def iperf_tcp_client_reverse(self):
        return

    def killall(self):
        return

    def transfer_logs(self):
        return

    """


class Server:
    def __init__(self, ip):
        self.name = 'S'
        self.ip = ip
        #self.logfile = initialize_logfile()

    def command(self, cmd):
        if type(cmd) is dict:
            msg = str(cmd)  # remember to eval and check for flags on other end (START, TIMEOUT, CMD, SUDO(?))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_ADDRESS, CONTROL_PORT))
        s.send(msg)
        response = s.recv(MSG_SIZE)
        print 'RECEIVED ', response
        s.close()
        res, run_num, pid = response.split(',')
        logcmd(msg, self.name)
        return res, run_num, pid


def test_cmd(dev, cmd):
    dev.command(cmd)
    return


"""
def experiment(S,R,C, exp):
    print "only fpings no traffic for 10 sec"
    run_number = pings_and_tcpdump(S,R,C)
    radiotap_dump([R,C])
    # run experiment here
    experiment_comment = exp()

    print 'wait for 12 sec for completion else send kill'
    time.sleep(experiment_timeout+2)
    kill_and_transfer(S,R,C, run_number, experiment_comment)
    return 0
"""


class Experiment:
    def __init__(self, measurement_name=None):
        self.A = Client(CLIENT_ADDRESS)
        self.R = Router(ROUTER_ADDRESS_LOCAL, ROUTER_USER, ROUTER_PASS)
        self.S = Server(SERVER_ADDRESS)
        self.iface = self.get_default_interface()
        self.device_list = [self.A, self.R, self.S]
        self.run_number = 0
        self.collect_calibrate = False
        self.experiment_counter = 0
        if measurement_name is not None:
            self.unique_id = self.get_mac_address() + '_' + measurement_name
        else:
            self.unique_id = self.get_mac_address()
        self.create_monitor_interface()

    def increment_experiment_counter(self):
        self.experiment_counter += 1
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())), ": Run Number ", self.experiment_counter
        return

    def get_default_interface(self):
        iface = []
        try:
            route = subprocess.check_output('cat /proc/net/route', shell=True).split('\n')
            for interface in route:
                if interface != '':
                    x = interface.split('\t')
                    if x[3] == '0003' and x[2] != '00000000':
                        iface.append(x[0])
            print "iface ", iface
            if len(iface) == 1:
                return iface[0]
        except:
            return CLIENT_WIRELESS_INTERFACE_NAME
        return CLIENT_WIRELESS_INTERFACE_NAME


    def get_mac_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', self.iface[:15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1].replace(':', '')

    def get_folder_name_from_server(self):
        serv, run_number, pid = self.S.command({'CMD': 'echo "Bollocks!"', 'START': 1})
        self.run_number = run_number
        #print 'DEBUG: run_number ' + run_number
        return 0

    def create_monitor_interface(self):
        self.A.command({'CMD': 'iw dev '+ self.iface +'mon del'})
        self.R.command({'CMD': 'iw dev '+ROUTER_WIRELESS_INTERFACE_NAME+'mon del'})
        self.A.command({'CMD': 'iw dev mon0 del'})
        self.R.command({'CMD': 'iw dev mon0 del'})
        self.A.command({'CMD': 'iw dev '+self.iface+' interface add '+self.iface+'mon type monitor flags none'})
        self.R.command({'CMD': 'iw dev '+ROUTER_WIRELESS_INTERFACE_NAME+' interface add '+ROUTER_WIRELESS_INTERFACE_NAME+'mon type monitor flags none'})
        self.ifup_monitor_interface()
        return

    def ifup_monitor_interface(self):
        self.A.command({'CMD': 'ifconfig '+self.iface+'mon up'})
        self.R.command({'CMD': 'ifconfig '+ROUTER_WIRELESS_INTERFACE_NAME+'mon up'})
        return

    def radiotap_dump(self, state, timeout):
        return

    def tcpdump_radiotapdump(self, state, timeout):
        # weird bug with R.command(tcpdump) -> doesn't work with &
        # also seems like timeout only kills the bash/sh -c process but not tcpdump itself - no wonder it doesn't work!
        self.S.command({'CMD':'tcpdump -s 100 -i '+SERVER_INTERFACE_NAME+' -w /tmp/browserlab/tcpdump_S'+state+'.pcap', 'TIMEOUT': timeout})
        # dump at both incoming wireless and outgoing eth1 for complete picture
        self.R.command({'CMD':'tcpdump -s 100 -i '+ROUTER_WIRELESS_INTERFACE_NAME+' eth1 -w /tmp/browserlab/tcpdump_R'+state+'.pcap'})
        self.R.command({'CMD':'tcpdump -i '+ROUTER_WIRELESS_INTERFACE_NAME+'mon -s 0 -p -U -w /tmp/browserlab/radio_R'+state+'.pcap'})
        #self.A.command({'CMD':'tcpdump -s 100 -i '+CLIENT_WIRELESS_INTERFACE_NAME+' -w /tmp/browserlab/tcpdump_A'+state+'.pcap', 'TIMEOUT': timeout})
        self.A.command({'CMD':'tcpdump -s 100 -i '+self.iface+' -w /tmp/browserlab/tcpdump_A'+state+'.pcap &'})
        self.A.command({'CMD':'tcpdump -i '+self.iface+'mon -s 0 -p -U -w /tmp/browserlab/radio_A'+state+'.pcap &'})
        return

    def ping_all(self):
        self.S.command({'CMD':'fping '+ROUTER_ADDRESS_GLOBAL+' -p 100 -c '+ str(2 * experiment_timeout * 10) + ' -r 1 -A > /tmp/browserlab/fping_S.log &'})
        self.S.command({'CMD':'fping '+CLIENT_ADDRESS+' -p 100 -c '+ str(2 * experiment_timeout * 10) + ' -r 1 -A > /tmp/browserlab/fping_S2.log &'})
        #self.R.command({'CMD':'fping '+CLIENT_ADDRESS+' '+ SERVER_ADDRESS +' -p 100 -l -r 1 -A >> /tmp/browserlab/fping_R.log &'})
        self.R.command({'CMD':'fping '+CLIENT_ADDRESS+' '+ SERVER_ADDRESS +' -p 100 -c '+ str(2 * experiment_timeout * 10) + ' -r 1 -A > /tmp/browserlab/fping_R.log &'})
        self.A.command({'CMD':'fping '+ROUTER_ADDRESS_LOCAL+' '+ SERVER_ADDRESS +' -p 100 -c '+ str(2 * experiment_timeout * 10) + ' -r 1 -A > /tmp/browserlab/fping_A.log &'})
        return

    def process_log(self, comment):
        poll_freq = 1
        ctr_len = str(int(experiment_timeout/poll_freq))

        for dev in [self.S, self.R, self.A]:
            #dev.command({'CMD':'for i in {1..'+ctr_len+'}; do top -b -n1 >> /tmp/browserlab/top_'+dev.name+'.log; sleep '+str(poll_freq)+'; done &'})
            dev.command({'CMD':'echo "$(date): ' + comment + '" >> /tmp/browserlab/top_'+dev.name+'.log;'})
            dev.command({'CMD':'top -b -n1 >> /tmp/browserlab/top_'+dev.name+'.log;'})
        return

    def interface_log(self, comment):
        poll_freq = 1
        ctr_len = str(int(experiment_timeout/poll_freq))

        #ifconfig (byte counters) for S
        #self.S.command({'CMD':'for i in {1..'+ctr_len+'}; do ifconfig >> /tmp/browserlab/ifconfig_'+self.S.name+'.log; sleep '+str(poll_freq)+'; done &'})
        self.S.command({'CMD':'echo "$(date): ' + comment + '" >> /tmp/browserlab/ifconfig_'+self.S.name+'.log;'})
        self.S.command({'CMD':'ifconfig >> /tmp/browserlab/ifconfig_'+self.S.name+'.log'})

        #iw dev (radiotap info) for wireless
        #self.R.command({'CMD':'for i in {1..'+ctr_len+'}; do iw dev '+ROUTER_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iwdev_'+self.R.name+'.log; sleep '+str(poll_freq)+'; done &'})
        #self.A.command({'CMD':'for i in {1..'+ctr_len+'}; do iw dev '+CLIENT_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iwdev_'+self.A.name+'.log; sleep '+str(poll_freq)+'; done &'})
        self.R.command({'CMD':'echo "$(date): ' + comment + '" >> /tmp/browserlab/ifconfig_'+self.R.name+'.log;'})
        self.R.command({'CMD':'iw dev '+ROUTER_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iwdev_'+self.R.name+'.log'})
        self.A.command({'CMD':'echo "$(date): ' + comment + '" >> /tmp/browserlab/ifconfig_'+self.A.name+'.log;'})
        self.A.command({'CMD':'iw dev '+self.iface+' station dump >> /tmp/browserlab/iwdev_'+self.A.name+'.log'})
        return

    def kill_all(self):
        self.S.command({'CMD': 'killall fping'}) #should be done with pid instead
        self.S.command({'CMD': 'killall tcpdump'})
        self.S.command({'CMD': 'killall iperf'})

        self.A.command({'CMD': 'killall fping'}) #should be done with pid instead
        self.A.command({'CMD': 'killall tcpdump'})
        self.A.command({'CMD': 'killall iperf'})

        self.R.command({'CMD': 'killall fping'}) #should be done with pid instead
        self.R.command({'CMD': 'killall tcpdump'})
        self.R.command({'CMD': 'killall iperf'})
        return

    def clear_all(self, close_R=1):
        self.S.command({'CMD': 'rm -rf /tmp/browserlab/*'})
        self.R.command({'CMD': 'rm -rf /tmp/browserlab/*'})
        self.A.command({'CMD': 'rm -rf /tmp/browserlab/*.log'})
        self.A.command({'CMD': 'rm -rf /tmp/browserlab/*.pcap'})
        if close_R:
            self.R.host.close()
        return

    def transfer_logs(self, run_number, comment):
        self.S.command({'CMD': 'mkdir -p /home/browserlab/'+self.unique_id+'/'+run_number+'_'+comment})
        self.S.command({'CMD':'cp /tmp/browserlab/*.log /home/browserlab/'+self.unique_id+'/'+run_number+'_'+comment})
        self.S.command({'CMD':'cp /tmp/browserlab/*.pcap /home/browserlab/'+self.unique_id+'/'+run_number+'_'+comment})

        self.A.command({'CMD': 'mkdir -p /tmp/browserlab/'+run_number+'_'+comment}) # instead of time use blocking resource to sync properly
        self.A.command({'CMD':'cp /tmp/browserlab/*.log /tmp/browserlab/'+run_number+'_'+comment+'/'})
        self.A.command({'CMD':'cp /tmp/browserlab/*.pcap /tmp/browserlab/'+run_number+'_'+comment+'/'})

        self.A.command({'CMD':'sshpass -p '+ ROUTER_PASS +' scp -o StrictHostKeyChecking=no '+ ROUTER_USER + '@' + ROUTER_ADDRESS_LOCAL + ':/tmp/browserlab/* /tmp/browserlab/'+run_number+'_'+comment+'/'})

        self.R.command({'CMD':'rm -rf /tmp/browserlab/*.pcap'})
        self.R.command({'CMD':'rm -rf /tmp/browserlab/*.log'})
        self.A.command({'CMD':'rm -rf /tmp/browserlab/*.pcap'})
        self.A.command({'CMD':'rm -rf /tmp/browserlab/*.log'})
        self.S.command({'CMD':'rm -rf /tmp/browserlab/*.pcap'})
        self.S.command({'CMD':'rm -rf /tmp/browserlab/*.log'})

        self.S.command({'CMD': 'chown -R browserlab.browserlab /home/browserlab/'+self.unique_id+'/'+run_number+'_'+comment})
        self.S.command({'CMD': 'chmod -R 777 /home/browserlab/'+self.unique_id+'/'+run_number+'_'+comment})
        self.A.command({'CMD': 'sshpass -p passw0rd scp -o StrictHostKeyChecking=no -r /tmp/browserlab/'+run_number+'_'+comment+' browserlab@' + SERVER_ADDRESS + ':'+self.unique_id})

        return

    def passive(self, comment, timeout):
        '''
        comment = 'before', 'during', 'after', 'calibrate'
        sleep_timeout = experiment_timeout, passive_timeout, calibrate_timeout
        '''
        self.tcpdump_radiotapdump(comment, timeout)
        #self.radiotap_dump(comment, timeout)

        print '\nDEBUG: Sleep for ' + str(timeout) + ' seconds as '+comment+' runs\n'
        time.sleep(timeout)

        self.kill_all()
        return

    def run_experiment(self, exp):
        self.get_folder_name_from_server()

        #self.passive('before', passive_timeout)

        timeout = 3 * experiment_timeout      # 30 sec

        self.tcpdump_radiotapdump('', experiment_timeout)
        #self.radiotap_dump('', experiment_timeout)

        state = 'before'
        print "DEBUG: "+str(time.time())+" state = " + state
        time.sleep(experiment_timeout)

        self.ping_all()
        self.process_log(state)
        self.interface_log(state)

        state = 'during'
        print "DEBUG: "+str(time.time())+" state = " + state
        comment = exp()
        print '\nDEBUG: Sleep for ' + str(timeout) + ' seconds as ' + comment + ' runs\n'
        time.sleep(2 * experiment_timeout)

        state = 'after'
        print "DEBUG: "+str(time.time())+" state = " + state
        self.process_log(state)
        self.interface_log(state)

        self.kill_all()
        #self.passive('after', passive_timeout)
        self.transfer_logs(self.run_number, comment)
        return

    def run_calibrate(self):
        self.get_folder_name_from_server()
        self.passive('calibrate', calibrate_timeout)
        self.transfer_logs(self.run_number, 'calibrate')
        return


    # EXPERIMENTS
    # passed as args into run_experiment()
    def no_traffic(self):
        return 'no_tra'

    def iperf_tcp_up_AR(self):
        self.R.command({'CMD': 'iperf -s -y C >> /tmp/browserlab/iperf_AR_R.log &'})
        self.A.command({'CMD': 'iperf -c ' + ROUTER_ADDRESS_LOCAL + ' -y C -i 0.5 >> /tmp/browserlab/iperf_AR_A.log &'})
        return 'AR_tcp'

    def iperf_tcp_dw_RA(self):
        self.A.command({'CMD': 'iperf -s -y C >> /tmp/browserlab/iperf_RA_A.log &'})
        self.R.command({'CMD': 'iperf -c ' + CLIENT_ADDRESS + ' -y C -i 0.5 >> /tmp/browserlab/iperf_RA_R.log &'})
        return 'RA_tcp'

    def iperf_tcp_up_RS(self):
        self.S.command({'CMD': 'iperf -s -y C >> /tmp/browserlab/iperf_RS_S.log &'})
        self.R.command({'CMD': 'iperf -c ' + SERVER_ADDRESS + ' -y C -i 0.5 >> /tmp/browserlab/iperf_RS_R.log &'})
        return 'RS_tcp'

    def iperf_tcp_dw_SR(self):
        self.R.command({'CMD': 'iperf -s -y C >> /tmp/browserlab/iperf_SR_R.log &'})
        self.S.command({'CMD': 'iperf -c ' + ROUTER_ADDRESS_GLOBAL + ' -y C -i 0.5 >> /tmp/browserlab/iperf_SR_S.log &'})
        return 'SR_tcp'

    def iperf_tcp_up_AS(self):
        self.S.command({'CMD': 'iperf -s -y C >> /tmp/browserlab/iperf_AS_S.log &'})
        self.A.command({'CMD': 'iperf -c ' + SERVER_ADDRESS + ' -y C -i 0.5 >> /tmp/browserlab/iperf_AS_A.log &'})
        return 'AS_tcp'

    def iperf_tcp_dw_SA(self):
        #NOTE this requires iperf reverse installed on client and server
        self.S.command({'CMD': 'iperf -s -y C -i 0.5 -t 10 --reverse >> /tmp/browserlab/iperf_SA_S.log &'})
        self.A.command({'CMD': 'iperf -c ' + SERVER_ADDRESS + ' -y C --reverse >> /tmp/browserlab/iperf_SA_A.log &'})
        return 'SA_tcp'

    def netperf_tcp_up_AR(self):
        # v2.4.5; default port 12865; reverse tcp stream RA
        # instead we can switch on all netservers on A and S initially.
        self.A.command({'CMD': 'netserver'})
        self.R.command({'CMD': 'netperf -t TCP_MAERTS -P 0 -f k -c -l 10 -H ' + CLIENT_ADDRESS + ' >> /tmp/browserlab/netperf_AR_R.log &'})
        return 'AR_tcp'

    def netperf_tcp_up_RS(self):
        # reverse tcp stream RS
        self.S.command({'CMD': 'netserver'})
        self.R.command({'CMD': 'netperf -t TCP_STREAM -P 0 -f k -c -l 10 -H ' + SERVER_ADDRESS + ' >> /tmp/browserlab/netperf_RS_R.log &'})
        return 'RS_tcp'

    def netperf_tcp_up_AS(self):
        # reverse tcp stream AS
        self.S.command({'CMD': 'netserver'})
        self.A.command({'CMD': 'netperf -t TCP_STREAM -P 0 -f k -c -l 10 -H ' + SERVER_ADDRESS + ' >> /tmp/browserlab/netperf_AS_A.log &'})

    def netperf_tcp_dw_RA(self):
        # v2.4.5; default port 12865; tcp stream RA
        self.A.command({'CMD': 'netserver'})
        self.R.command({'CMD': 'netperf -t TCP_STREAM -P 0 -f k -c -l 10 -H ' + CLIENT_ADDRESS + ' >> /tmp/browserlab/netperf_RA_R.log &'})
        return 'RA_tcp'

    def netperf_tcp_dw_SR(self):
        # reverse tcp stream RS
        self.S.command({'CMD': 'netserver'})
        self.R.command({'CMD': 'netperf -t TCP_MAERTS -P 0 -f k -c -l 10 -H ' + SERVER_ADDRESS + ' >> /tmp/browserlab/netperf_SR_R.log &'})
        return 'SR_tcp'

    def netperf_tcp_dw_SA(self):
        # reverse tcp stream AS
        self.S.command({'CMD': 'netserver'})
        self.A.command({'CMD': 'netperf -t TCP_MAERTS -P 0 -f k -c -l 10 -H ' + SERVER_ADDRESS + ' >> /tmp/browserlab/netperf_SA_A.log &'})
        return 'SA_tcp'

    # udpprobe gives both up and dw
    def probe_udp_AR(self):
        self.R.command({'CMD': 'udpprobeserver >> /tmp/browserlab/probe_AR_R.log &'})
        self.A.command({'CMD': 'udpprober -s ' + ROUTER_ADDRESS_LOCAL + ' >> /tmp/browserlab/probe_AR_A.log &'})
        return 'AR_udp'

    def probe_udp_RS(self):
        self.S.command({'CMD': 'udpprobeserver >> /tmp/browserlab/probe_RS_S.log &'})
        self.R.command({'CMD': 'udpprober -s ' + SERVER_ADDRESS + ' >> /tmp/browserlab/probe_RS_R.log &'})
        return 'RS_udp'

    def probe_udp_AS(self):
        self.S.command({'CMD': 'udpprobeserver >> /tmp/browserlab/probe_AS_S.log &'})
        self.A.command({'CMD': 'udpprober -s ' + SERVER_ADDRESS + ' >> /tmp/browserlab/probe_AS_A.log &'})
        return 'AS_udp'

    def ABWprobe(self):
        #TODO
        return
