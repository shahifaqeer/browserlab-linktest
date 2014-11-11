#!/usr/bin/env python

from __future__ import division
#from datetime import datetime
#from random import randint
from classes import Router, Client, Server
#from parsers import MyParser
from collections import defaultdict

import numpy as np
import time
import socket
import subprocess
#import shlex
import struct
import fcntl
import sys
import traceback

import const


CONTROL_PORT = const.CONTROL_PORT


def test_cmd(dev, cmd):
    dev.command(cmd)
    return


class Experiment:
    def __init__(self, measurement_name=None):
        self.A = Client(const.CLIENT_ADDRESS)
        self.R = Router(const.ROUTER_ADDRESS_LOCAL, const.ROUTER_USER, const.ROUTER_PASS)
        #self.B = Server(const.CLIENT_ADDRESS2)
        #self.B.name = 'B'
        self.S = Server(const.SERVER_ADDRESS)
        self.EXTRA_NODES = const.EXTRA_NODES
        if self.EXTRA_NODES:
            self.arrB = []
            for addr in const.EXTRA_NODE_ADDRESSES:
                self.arrB.append(Server(addr))
        self.check_connection()
        self.iface = self.get_default_interface()
        self.A.ip = self.get_ip_address(self.iface)
        self.device_list = [self.A, self.R, self.S]
        self.run_number = 0
        self.collect_calibrate = False
        self.experiment_counter = 0
        self.experiment_name = 'default'
        self.create_monitor_interface()
        self.set_unique_id(measurement_name)
        self.set_test_timeout(const.EXPERIMENT_TIMEOUT)

        self.kill_all(1)    #kill tcpdump, iperf, netperf, fping on all
        self.clear_all(0)   #clear /tmp/browserlab/* but don't close the connection to R

        self.set_config_options(const.METHOD)
        self.set_iperf_config_options()

        self.start_servers()

        self.probe_rate = defaultdict(int)
        self.set_udp_rate_mbit(const.INIT_ACCESS_RATE, const.INIT_HOME_RATE, const.INIT_BLAST_RATE)

    def set_config_options(self, method):
        # config options
        self.method = method
        self.USE_UDPPROBE = const.USE_UDPPROBE
        self.USE_IPERF_REV = const.USE_IPERF_REV
        self.USE_IPERF3 = const.USE_IPERF3
        self.USE_NETPERF = const.USE_NETPERF
        self.tcp = const.COLLECT_tcp
        self.udp = const.COLLECT_udp
        self.blast = const.COLLECT_udp_blast

        self.tcpdump = const.COLLECT_tcpdump
        self.non_blocking_experiment = const.NON_BLOCKING_EXP
        self.blk = not self.non_blocking_experiment
        self.before_timeout = const.BEFORE_TIMEOUT
        self.ping_timed = const.PING_TIMED
        self.DIFF_PING = const.DIFF_PING

        if self.non_blocking_experiment:
            self.experiment_suffix = ' &'
        else:
            self.experiment_suffix = ''

        return

    def set_iperf_config_options(self):
        # iperf config opions
        self.parallel = const.USE_PARALLEL_TCP
        self.num_parallel_streams = const.TCP_PARALLEL_STREAMS
        self.use_iperf_timeout = const.USE_IPERF_TIMEOUT
        self.num_bits_to_send = const.NUM_BITS_TO_SEND
        self.use_window_size = const.USE_WINDOW_SIZE
        if self.use_window_size:
            self.window_size = const.WINDOW_SIZE
        self.use_omit_n_sec = const.USE_OMIT_N_SEC
        if self.use_omit_n_sec:
            self.omit_n_sec = const.OMIT_N_SEC
        self.WTF_enable = const.WTF_ENABLE
        self.ROUTER_TCPDUMP_enable = const.ROUTER_TCP_DUMP

        return

    def start_servers(self):
        #if self.USE_UDPPROBE:
        #    self.start_shaperprobe_udp_servers()
        if self.USE_IPERF3:
            self.start_iperf3_servers()
        #if self.udp:
        #    self.start_iperf_rev_servers('udp')
        #if self.tcp:
        #    self.start_iperf_rev_servers('tcp')
        #if self.USE_NETPERF:
        #    self.start_netperf_servers()
        return

    def set_unique_id(self, measurement_name):
        if measurement_name is not None:
            self.unique_id = self.get_mac_address() + '_' + measurement_name
        else:
            self.unique_id = self.get_mac_address()
        return

    def check_connection(self, serv=None):
        if serv == None:
            serv = self.S

        cmd = {'CMD': 'echo "check port"'}
        if type(cmd) is dict:
            msg = str(cmd)  # remember to eval and check for flags on other end (START, TIMEOUT, CMD, SUDO(?))

        num_retries = 0
        port = const.CONTROL_PORT + num_retries % 5

        while num_retries<10:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((serv.ip, serv.port))
                s.send(msg)
                response = s.recv(const.MSG_SIZE)
                print 'RECEIVED ', response
                res = response
                #res, run_num, pid = response.split(',')
                s.close()
                print "DEBUG: connection successful to "+serv.ip + ":" + str(serv.port)
                return res#, run_num, pid
            except Exception, error:
                print "DEBUG: Can't connect to "+str(serv.ip)+":"+str(serv.port)+". \nRETRY "+str(num_retries+1)+" in 2 seconds."
                traceback.print_exc()
                num_retries += 1
                port = serv.port + num_retries % const.TOTAL_PORTS_TO_TRY    #try ports 12345 to 12349 twice each
                time.sleep(2)
                continue
            break
        raw_input("Server unresponsive. Press any key to exit. ")
        sys.exit()
        return

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
            if len(iface) == 1:
                if iface[0] != const.CLIENT_WIRELESS_INTERFACE_NAME:
                    cont = raw_input("The default interface for this device has changed from "+ const.CLIENT_WIRELESS_INTERFACE_NAME + " to "  + iface[0] +". Correct? (y/*)")
                    if cont == 'y':
                        return iface[0]
                    else:
                        return const.CLIENT_WIRELESS_INTERFACE_NAME
        except:
            return const.CLIENT_WIRELESS_INTERFACE_NAME
        return const.CLIENT_WIRELESS_INTERFACE_NAME

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ipaddr = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
            )[20:24])
        if const.CLIENT_ADDRESS != ipaddr:
            cont = raw_input("The default IP Address for this device has changed from "+ const.CLIENT_ADDRESS + " to "  + ipaddr +". Correct? (y/*)")
            if cont == 'y':
                return ipaddr
        return const.CLIENT_ADDRESS


    def get_mac_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', self.iface[:15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1].replace(':', '')

    def get_folder_name_from_server(self):
        #serv, run_number, pid = self.S.command({'CMD': 'echo "Bollocks!"', 'START': 1})
        run_number = self.S.command({'CMD': 'echo "Bollocks!"', 'START': 1})
        self.run_number = run_number
        #print 'DEBUG: run_number ' + run_number
        return 0

    def create_monitor_interface(self):
        self.A.command({'CMD': 'iw dev '+ self.iface +'mon del'})
        #self.B.command({'CMD': 'iw dev '+ self.iface +'mon del'})
        self.R.command({'CMD': 'iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+'mon del'})
        self.A.command({'CMD': 'iw dev '+self.iface+' interface add '+self.iface+'mon type monitor flags none'})
        #self.B.command({'CMD': 'iw dev '+self.iface+' interface add '+self.iface+'mon type monitor flags none'})
        self.R.command({'CMD': 'iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' interface add '+const.ROUTER_WIRELESS_INTERFACE_NAME+'mon type monitor flags none'})
        self.ifup_monitor_interface()
        return

    def ifup_monitor_interface(self):
        self.A.command({'CMD': 'ifconfig '+self.iface+'mon up'})
        #self.B.command({'CMD': 'ifconfig '+self.iface+'mon up'})
        self.R.command({'CMD': 'ifconfig '+const.ROUTER_WIRELESS_INTERFACE_NAME+'mon up'})
        return

    def tcpdump_radiotapdump(self, state, timeout):
        # weird bug with R.command(tcpdump) -> doesn't work with &
        # also seems like timeout only kills the bash/sh -c process but not tcpdump itself - no wonder it doesn't work!
        #if self.S.ip != '132.227.126.1':
        if timeout:
            self.S.command({'CMD':'/usr/sbin/tcpdump -s 200 -i '+const.SERVER_INTERFACE_NAME+' -w '+const.TMP_BROWSERLAB_PATH+'tcpdump_S'+state+'.pcap', 'TIMEOUT': timeout})
        else:
            self.S.command({'CMD':'/usr/sbin/tcpdump -s 200 -i '+const.SERVER_INTERFACE_NAME+' -w '+const.TMP_BROWSERLAB_PATH+'tcpdump_S'+state+'.pcap &'})
        # dump at both incoming wireless and outgoing eth1 for complete picture

        if self.experiment_name[:2] == 'RS' or self.experiment_name[:2] == 'SR':
            router_interface_name = 'eth1'
        else:
            router_interface_name = const.ROUTER_WIRELESS_INTERFACE_NAME

        if self.ROUTER_TCPDUMP_enable:
            if router_interface_name[:4] == const.GENERIC_WIRELESS_INTERFACE_NAME:    #wlan
                # take only radiotap
                self.R.command({'CMD':'tcpdump -i '+const.ROUTER_WIRELESS_INTERFACE_NAME+'mon -s 200 -p -U -w /tmp/browserlab/radio_R'+state+'.pcap'})
                # need this for WTF
                #self.R.command({'CMD':'tcpdump -s 100 -i br-lan -w /tmp/browserlab/tcpdump_R'+state+'.pcap'})
                # need this for buffer timing check
                #self.R.command({'CMD':'tcpdump -s 100 -i eth1 -w /tmp/browserlab/tcpdump_eth1_R'+state+'.pcap'})
            else:
                self.R.command({'CMD':'tcpdump -s 100 -i '+router_interface_name+' -w /tmp/browserlab/tcpdump_R'+state+'.pcap'})

        if self.WTF_enable:
            self.R.command({'CMD':'tcpdump -i br-lan -s 200 -p -U -w /tmp/browserlab/wtf_R'+state+'.pcap'})

        if self.iface[:4] == const.GENERIC_WIRELESS_INTERFACE_NAME:
            # take only radiotap
            self.A.command({'CMD':'tcpdump -i '+self.iface+'mon -s 200 -p -U -w /tmp/browserlab/radio_A'+state+'.pcap &'})
            #self.B.command({'CMD':'tcpdump -i '+self.iface+'mon -s 200 -p -U -w /tmp/browserlab/radio_B'+state+'.pcap &'})
        else:
            #self.A.command({'CMD':'tcpdump -s 100 -i '+const.CLIENT_WIRELESS_INTERFACE_NAME+' -w /tmp/browserlab/tcpdump_A'+state+'.pcap', 'TIMEOUT': timeout})
            self.A.command({'CMD':'tcpdump -s 100 -i '+self.iface+' -w /tmp/browserlab/tcpdump_A'+state+'.pcap &'})
            #self.B.command({'CMD':'tcpdump -s 100 -i '+self.iface+' -w /tmp/browserlab/tcpdump_B'+state+'.pcap &'})
        return

    def ping_all(self):
        if self.ping_timed:
            timeout = 2 * self.timeout      # 20 sec
            # ALWAYS pass fping with & not to thread - thread seems to be blocking
            self.S.command({'CMD':'fping '+const.ROUTER_ADDRESS_GLOBAL+' -p 100 -c '+ str(timeout * 10) + ' -b ' + const.PING_SIZE + ' -r 1 -A > '+const.TMP_BROWSERLAB_PATH+'fping_S.log &'})
            self.R.command({'CMD':'fping '+self.A.ip+' '+ const.SERVER_ADDRESS +' ' + const.ROUTER_ADDRESS_PINGS + ' -p 100 -c '+ str(timeout * 10) + ' -b ' + const.PING_SIZE + ' -r 1 -A > /tmp/browserlab/fping_R.log &'})
            self.A.command({'CMD':'fping '+const.ROUTER_ADDRESS_LOCAL+' '+ const.SERVER_ADDRESS +' ' + const.ROUTER_ADDRESS_PINGS + ' -p 100 -c '+ str(timeout * 10) + ' -b ' + const.PING_SIZE +  ' -r 1 -A > /tmp/browserlab/fping_A.log &'})
            #self.B.command({'CMD':'fping '+const.ROUTER_ADDRESS_LOCAL+' '+ const.SERVER_ADDRESS +' ' + self.A.ip + ' -p 100 -c '+ str(timeout * 10) + ' -b ' + const.PING_SIZE +  ' -r 1 -A > /tmp/browserlab/fping_B.log &'})
        else:
            self.S.command({'CMD':'fping '+const.ROUTER_ADDRESS_GLOBAL+' -p 100 -l -b ' + const.PING_SIZE + ' -r 1 -A > '+const.TMP_BROWSERLAB_PATH+'fping_S.log &'})
            self.R.command({'CMD':'fping '+self.A.ip+' '+ const.SERVER_ADDRESS +' ' + const.ROUTER_ADDRESS_PINGS + ' -p 100 -l -b ' + const.PING_SIZE + ' -r 1 -A > /tmp/browserlab/fping_R.log &'})
            self.A.command({'CMD':'fping '+const.ROUTER_ADDRESS_LOCAL+' '+ const.SERVER_ADDRESS +' ' + const.ROUTER_ADDRESS_PINGS + ' -p 100 -l -b ' + const.PING_SIZE +  ' -r 1 -A > /tmp/browserlab/fping_A.log &'})
            #self.B.command({'CMD':'fping '+const.ROUTER_ADDRESS_LOCAL+' '+ const.SERVER_ADDRESS +' ' + self.A.ip + ' -p 100 -l -b ' + const.PING_SIZE +  ' -r 1 -A > /tmp/browserlab/fping_B.log &'})

        return

    def differential_ping(self):
        if self.ping_timed:
            timeout = 2 * self.timeout      # 20 sec
            # ALWAYS pass fping with & not to thread - thread seems to be blocking
            self.A.command({'CMD':'fping '+const.ROUTER_ADDRESS_LOCAL+' '+ const.SERVER_ADDRESS +' ' + const.ROUTER_ADDRESS_PINGS + ' -p 100 -c '+ str(timeout * 10) + ' -b ' + const.PING_SIZE +  ' -r 1 -A > /tmp/browserlab/fping_A.log &'})
            #self.B.command({'CMD':'fping '+const.ROUTER_ADDRESS_LOCAL+' '+ const.SERVER_ADDRESS +' ' + self.A.ip + ' -p 100 -c '+ str(timeout * 10) + ' -b ' + const.PING_SIZE +  ' -r 1 -A > /tmp/browserlab/fping_B.log &'})
        else:
            self.A.command({'CMD':'fping '+const.ROUTER_ADDRESS_LOCAL+' '+ const.SERVER_ADDRESS +' ' + const.ROUTER_ADDRESS_PINGS + ' -p 100 -l -b ' + const.PING_SIZE +  ' -r 1 -A > /tmp/browserlab/fping_A.log &'})
            #self.B.command({'CMD':'fping '+const.ROUTER_ADDRESS_LOCAL+' '+ const.SERVER_ADDRESS +' ' + self.A.ip + ' -p 100 -l -b ' + const.PING_SIZE +  ' -r 1 -A > /tmp/browserlab/fping_B.log &'})

        return


    def start_netperf_servers(self):
        if const.SERVER_ADDRESS == '132.227.126.1':
            self.S.command({'CMD': './netserver -p '+const.NETPERF_PORT})
            self.R.command({'CMD': 'netserver -p '+const.NETPERF_PORT})
            #self.B.command({'CMD': 'netserver -p '+const.NETPERF_PORT})
            self.A.command({'CMD': 'netserver -p '+const.NETPERF_PORT})
        else:
            self.S.command({'CMD': 'netserver -p '+const.NETPERF_PORT})
            self.R.command({'CMD': 'netserver -p '+const.NETPERF_PORT})
            #self.B.command({'CMD': 'netserver -p '+const.NETPERF_PORT})
            self.A.command({'CMD': 'netserver -p '+const.NETPERF_PORT})
        return

    def start_iperf3_servers(self):
        if const.USE_IPERF3:
            rx = self.S
            rx.command({'CMD': 'iperf3 -s -p '+const.PERF_PORT+' -J >> '+const.TMP_BROWSERLAB_PATH+'iperf3_server_'+rx.name+'.log &'})
            rx = self.R
            rx.command({'CMD': 'iperf3 -s -p '+const.PERF_PORT+' -J >> /tmp/browserlab/iperf3_server_'+rx.name+'.log'})
            rx = self.A
            rx.command({'CMD': 'iperf3 -s -p '+const.PERF_PORT+' -J >> /tmp/browserlab/iperf3_server_'+rx.name+'.log &'})
            #rx = self.B
            #rx.command({'CMD': 'iperf3 -s -p '+const.PERF_PORT+' -J >> /tmp/browserlab/iperf3_server_'+rx.name+'.log &'})
        else:
            for rx in [self.R, self.A]: #, self.B]:
                rx.command({'CMD': 'iperf -s -u -f k -y C >> /tmp/browserlab/iperf_udp_server_'+rx.name+'.log &'})
            rx = self.S
            rx.command({'CMD': 'iperf -s -u -f k -y C >> '+const.TMP_BROWSERLAB_PATH+'iperf_udp_server_'+rx.name+'.log &'})
        return

    def start_iperf_rev_servers(self, proto):
        if proto == 'udp':
            for rx in [self.R, self.A]: #, self.B]:
                rx.command({'CMD': 'iperf -s -u -p '+ const.IPERF_UDP_PORT +' >> /tmp/browserlab/iperf_udp_server_'+rx.name+'.log &'})
            rx = self.S
            rx.command({'CMD': 'iperf -s -u -p '+ const.IPERF_UDP_PORT +' >> '+const.TMP_BROWSERLAB_PATH+'iperf_udp_server_'+rx.name+'.log &'})
        elif proto == 'tcp':
            for rx in [self.R, self.A]: #, self.B]:
                rx.command({'CMD': 'iperf -s -p '+ const.IPERF_TCP_PORT+' >> /tmp/browserlab/iperf_tcp_server_'+rx.name+'.log &'})
            rx = self.S
            rx.command({'CMD': 'iperf -s -p '+const.IPERF_TCP_PORT+' >> '+const.TMP_BROWSERLAB_PATH+'iperf_tcp_server_'+rx.name+'.log &'})
        return

    def start_iperf_servers(self):
        if not const.USE_IPERF3:
            for rx in [self.R, self.A]: #, self.B]:
                rx.command({'CMD': 'iperf -s -u >> /tmp/browserlab/iperf_udp_server_'+rx.name+'.log &'})
            rx = self.S
            self.S.command({'CMD': 'iperf -s -u >> '+const.TMP_BROWSERLAB_PATH+'iperf_udp_server_'+rx.name+'.log &'})
        return

    def start_shaperprobe_udp_servers(self):
        for rx in [self.R, self.A]: #, self.B]:
            rx.command({'CMD': 'udpprobeserver >> /tmp/browserlab/probe_server_'+rx.name+'.log &'})
        self.S.command({'CMD': 'udpprobeserver >> '+const.TMP_BROWSERLAB_PATH+'probe_server_'+self.S.name+'.log &'})
        return

    def convert_sar_to_log(self):
        for dev in [self.R, self.A]: #, self.B]:
            dev.command({'CMD':'sar -f /tmp/browserlab/sar_' + dev.name + '.out > /tmp/browserlab/sar_' + dev.name + '.log;rm -rf /tmp/browserlab/sar_' + dev.name + '.out'})
        dev = self.S
        dev.command({'CMD':'sar -f '+const.TMP_BROWSERLAB_PATH+'sar_' + dev.name + '.out > '+const.TMP_BROWSERLAB_PATH+'sar_' + dev.name + '.log;rm -rf '+const.TMP_BROWSERLAB_PATH+'sar_' + dev.name + '.out'})
        return

    def active_logs(self, nrepeats, delta_time=1):
        nrepeats = str(nrepeats)
        delta_time = str(delta_time)
        self.S.command({'CMD': 'nohup sar -o '+const.TMP_BROWSERLAB_PATH+'sar_S.out ' + delta_time + ' ' + nrepeats + ' >/dev/null 2>&1 &'})
        self.R.command({'CMD': 'sar -o /tmp/browserlab/sar_R.out ' + delta_time + ' ' + nrepeats + ' >/dev/null 2>&1 &'})
        self.A.command({'CMD': 'nohup sar -o /tmp/browserlab/sar_A.out ' + delta_time + ' ' + nrepeats + ' >/dev/null 2>&1 &'})
        #self.B.command({'CMD': 'nohup sar -o /tmp/browserlab/sar_B.out ' + delta_time + ' ' + nrepeats + ' >/dev/null 2>&1 &'})

        self.S.command({'CMD':'for i in $(seq 1 1 '+nrepeats+');do\
        echo "$i: $(date)" >> '+const.TMP_BROWSERLAB_PATH+'ifconfig_S.log;\
        /sbin/ifconfig  >> '+const.TMP_BROWSERLAB_PATH+'ifconfig_S.log;\
        sleep ' + delta_time + '; done &'})

        self.R.command({'CMD':'for i in $(seq 1 1 '+nrepeats+');do\
        echo "$i: $(date)" >> /tmp/browserlab/iw_R.log;\
        iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' survey dump >> /tmp/browserlab/iw_R.log;\
        iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iw_R.log;\
        ifconfig >> /tmp/browserlab/iw_R.log;\
        sleep ' + delta_time + '; done &'})

        #self.B.command({'CMD':'for i in $(seq 1 1 '+nrepeats+');do\
        #echo "$i: $(date)" >> /tmp/browserlab/iw_B.log;\
        #iw dev '+const.CLIENT_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iw_B.log;\
        #sleep ' + delta_time + '; done &'})

        self.A.command({'CMD':'for i in $(seq 1 1 '+nrepeats+');do\
        echo "$i: $(date)" >> /tmp/browserlab/iw_A.log;\
        iw dev '+const.CLIENT_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iw_A.log;\
        sleep ' + delta_time + '; done &'})
        return

    def process_log(self, comment):
        poll_freq = 1
        ctr_len = str(int(self.timeout/poll_freq))

        for dev in [self.S, self.R, self.A]: #, self.B]:
            #dev.command({'CMD':'for i in {1..'+ctr_len+'}; do top -b -n1 >> /tmp/browserlab/top_'+dev.name+'.log; sleep '+str(poll_freq)+'; done &'})
            dev.command({'CMD':'echo "$(date): ' + comment + '" >> /tmp/browserlab/top_'+dev.name+'.log;top -b -n1 >> /tmp/browserlab/top_'+dev.name+'.log;'})
        return

    def interface_log(self, comment):
        poll_freq = 1
        ctr_len = str(int(self.timeout/poll_freq))

        #ifconfig (byte counters) for S
        #self.S.command({'CMD':'for i in {1..'+ctr_len+'}; do ifconfig >> /tmp/browserlab/ifconfig_'+self.S.name+'.log; sleep '+str(poll_freq)+'; done &'})
        self.S.command({'CMD':'echo "$(date): ' + comment + '" >> '+const.TMP_BROWSERLAB_PATH+'ifconfig_'+self.S.name+'.log;/sbin/ifconfig >> '+const.TMP_BROWSERLAB_PATH+'ifconfig_'+self.S.name+'.log'})

        #iw dev (radiotap info) for wireless
        #self.R.command({'CMD':'for i in {1..'+ctr_len+'}; do iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iwdev_'+self.R.name+'.log; sleep '+str(poll_freq)+'; done &'})
        #self.A.command({'CMD':'for i in {1..'+ctr_len+'}; do iw dev '+self.iface+' station dump >> /tmp/browserlab/iwdev_'+self.A.name+'.log; sleep '+str(poll_freq)+'; done &'})
        self.R.command({'CMD':'echo "$(date): ' + comment + '" >> /tmp/browserlab/iwdev_'+self.R.name+'.log;iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iwdev_'+self.R.name+'.log'})
        #self.B.command({'CMD':'echo "$(date): ' + comment + '" >> /tmp/browserlab/iwdev_'+self.B.name+'.log;iw dev '+self.iface+' station dump >> /tmp/browserlab/iwdev_'+self.B.name+'.log'})
        self.A.command({'CMD':'echo "$(date): ' + comment + '" >> /tmp/browserlab/iwdev_'+self.A.name+'.log;iw dev '+self.iface+' station dump >> /tmp/browserlab/iwdev_'+self.A.name+'.log'})
        return

    def airtime_util_log(self, comment, poll_freq=1):
        ctr_len = str(int(self.timeout/poll_freq))
        if comment == 'during':
            self.R.command({'CMD':'for i in (seq 1 1 '+ctr_len+'); do iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' survey dump >> /tmp/browserlab/iwsurvey_'+self.R.name+'.log; sleep '+str(poll_freq)+'; done &'})
        return

    def kill_all(self, all_proc = 0):
        for node in [self.A, self.R, self.S]: #self.B, self.S]:
            node.command({'CMD': 'killall tcpdump;killall fping'})
            if all_proc:
                node.command({'CMD': 'killall iperf;killall iperf3;killall netperf'})
        return

    def clear_all(self, close_R=0):
        self.S.command({'CMD': 'rm -rf '+const.TMP_BROWSERLAB_PATH+'*'})
        self.R.command({'CMD': 'rm -rf /tmp/browserlab/*'})
        #self.B.command({'CMD': 'rm -rf /tmp/browserlab/*.log;rm -rf /tmp/browserlab/*.pcap'})
        self.A.command({'CMD': 'rm -rf /tmp/browserlab/*.log;rm -rf /tmp/browserlab/*.pcap'})
        if close_R:
            self.R.host.close()
        return

    def transfer_logs(self, run_number, comment):
        self.convert_sar_to_log()

        self.S.command({'CMD':'mkdir -p '+const.TMP_DATA_PATH+self.unique_id+'/'+run_number+'_'+comment})
        self.S.command({'CMD':'cp '+const.TMP_BROWSERLAB_PATH+'*.log '+const.TMP_DATA_PATH+self.unique_id+'/'+run_number+'_'+comment+';\
                        cp '+const.TMP_BROWSERLAB_PATH+'*.pcap '+const.TMP_DATA_PATH+self.unique_id+'/'+run_number+'_'+comment})

        self.A.command({'CMD': 'mkdir -p /tmp/browserlab/'+run_number+'_'+comment}) # instead of time use blocking resource to sync properly
        self.A.command({'CMD':'cp /tmp/browserlab/*.log /tmp/browserlab/'+run_number+'_'+comment+'/;\
                        cp /tmp/browserlab/*.pcap /tmp/browserlab/'+run_number+'_'+comment+'/'})

        self.A.command({'CMD':'sshpass -p '+ const.ROUTER_PASS +' scp -o StrictHostKeyChecking=no '+ const.ROUTER_USER + '@' + const.ROUTER_ADDRESS_LOCAL + ':/tmp/browserlab/* /tmp/browserlab/'+run_number+'_'+comment+'/'})
        # from B
        #self.A.command({'CMD':'sshpass -p '+ const.CLIENT2_PASS +' scp -o StrictHostKeyChecking=no '+ const.CLIENT2_USER + '@' + const.CLIENT_ADDRESS2 + ':/tmp/browserlab/* /tmp/browserlab/'+run_number+'_'+comment+'/'})
        #self.B.command({'CMD':'rm -rf /tmp/browserlab/*.pcap;rm -rf /tmp/browserlab/*.log'})

        self.R.command({'CMD':'rm -rf /tmp/browserlab/*.pcap;rm -rf /tmp/browserlab/*.log'})
        self.A.command({'CMD':'rm -rf /tmp/browserlab/*.pcap;rm -rf /tmp/browserlab/*.log'})
        self.S.command({'CMD':'rm -rf '+const.TMP_BROWSERLAB_PATH+'*.pcap;rm -rf '+const.TMP_BROWSERLAB_PATH+'*.log'})

        #self.S.command({'CMD': 'chown -R browserlab:browserlab /home/browserlab/'+self.unique_id+'/'+run_number+'_'+comment})
        #self.S.command({'CMD': 'chmod -R 777 /home/browserlab/'+self.unique_id+'/'+run_number+'_'+comment})
        #self.A.command({'CMD': 'sshpass -p passw0rd scp -o StrictHostKeyChecking=no -r /tmp/browserlab/'+run_number+'_'+comment+' browserlab@' + const.SERVER_ADDRESS + ':'+self.unique_id})
        self.A.command({'CMD': 'mkdir -p /tmp/data/' + self.unique_id})
        self.A.command({'CMD': 'mv -f /tmp/browserlab/* /tmp/data/' + self.unique_id + '/'})

        return

    def transfer_all_later(self):
        #self.A.command({'CMD': 'sshpass -p passw0rd scp -o StrictHostKeyChecking=no -r /tmp/data/' +self.unique_id+ '/* browserlab@' + const.SERVER_ADDRESS + ':'+self.unique_id})
        self.A.command({'CMD': 'sshpass -p passw0rd scp -o StrictHostKeyChecking=no -r /tmp/data/' +self.unique_id+ ' '+const.DATA_SERVER_PATH})
        #rsync --rsh="sshpass -p passw0rd ssh -l browserlab" const.TMP_DATA_PATH:/var/www/html/ /backup/
        self.S.command({'CMD': 'scp -o StrictHostKeyChecking=no -r '+const.TMP_DATA_PATH+self.unique_id+'/* '+const.DATA_SERVER_PATH+self.unique_id+'/'})
        return

    def passive(self, comment, timeout):
        '''
        comment = 'before', 'during', 'after', 'calibrate'
        sleep_timeout = self.timeout, const.PASSIVE_TIMEOUT, const.CALIBRATE_TIMEOUT
        '''
        self.tcpdump_radiotapdump(comment, timeout)
        #self.radiotap_dump(comment, timeout)

        print '\nDEBUG: Sleep for ' + str(timeout) + ' seconds as '+comment+' runs ' +str(self.experiment_counter) + '\n'
        time.sleep(timeout)

        self.kill_all()
        return

    def set_udp_rate_mbit(self, rate_access, rate_home=100, rate_blast=1000):
        self.rate_access = str(rate_access)
        self.rate_home = str(rate_home)
        self.rate_blast = str(rate_blast)
        return

    def set_test_timeout(self, timeout=const.EXPERIMENT_TIMEOUT):
        self.timeout = timeout
        return

    def run_experiment(self, exp, exp_name):
        self.experiment_name = exp_name #same as comment

        self.get_folder_name_from_server()

        if self.tcpdump == 1:
            self.tcpdump_radiotapdump('', 0)

        nrepeats = 2 + int(self.timeout) + 2
        self.active_logs(nrepeats)

        state = 'before'
        print "DEBUG: "+str(time.time())+" state = " + state
        timeout = self.before_timeout
        time.sleep(timeout)
        print '\nDEBUG: Sleep for ' + str(timeout) + ' seconds as dump runs '+ str(self.experiment_counter) +'\n'

        self.ping_all()

        timeout = 2 * self.timeout        # 20 sec
        if exp_name == 'SR_fab':
            timeout = 4 * self.timeout    # 40 sec

        state = 'during'
        print "DEBUG: "+str(time.time())+" state = " + state
        comment = exp()
        if self.non_blocking_experiment:
            time.sleep(timeout)
        print '\nDEBUG: Sleep for ' + str(timeout) + ' seconds as ' + comment + ' runs '+ str(self.experiment_counter) +'\n'

        state = 'after'
        print "DEBUG: "+str(time.time())+" state = " + state

        self.kill_all(1)
        self.transfer_logs(self.run_number, comment)

        #hack to start udp servers for next round
        self.start_servers()
        #self.start_iperf3_servers()
        #if self.udp == 1:
        #    self.start_shaperprobe_udp_servers()

        return

    def run_calibrate(self):
        self.get_folder_name_from_server()
        self.passive('calibrate', const.CALIBRATE_TIMEOUT)
        self.transfer_logs(self.run_number, 'calibrate')
        return


    # EXPERIMENTS
    # passed as args into run_experiment()
    def run_udpprobe(self, exp, exp_name):
        self.exp_name = exp_name
        self.get_folder_name_from_server()

        nrepeats = 2 + int(self.timeout) + 2
        self.active_logs(nrepeats)

        state = 'before'
        print "DEBUG: "+str(time.time())+" state = " + state
        timeout=self.before_timeout
        time.sleep(timeout)
        print '\nDEBUG: Sleep for ' + str(timeout) + ' seconds as dump runs '+ str(self.experiment_counter) +'\n'

        state = 'during'
        print "DEBUG: "+str(time.time())+" state = " + state
        comment = exp()
        if self.non_blocking_experiment:
            time.sleep(const.PROBE_TIMEOUT)
        print '\nDEBUG: Sleep for ' + str(const.PROBE_TIMEOUT) + ' seconds as ' + comment + ' runs '+ str(self.experiment_counter) +'\n'

        state = 'after'
        print "DEBUG: "+str(time.time())+" state = " + state

        self.kill_all(1)
        self.transfer_logs(self.run_number, comment)

        #hack to start udp servers for next round
        self.start_servers()

        return

    def run_only_experiment(self, exp, exp_name):

        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run "+ exp_name + " " + str(self.experiment_counter)
        self.experiment_name = exp_name #same as comment
        state = exp_name
        timeout = self.timeout
        self.get_folder_name_from_server()

        if self.tcpdump == 1:
            self.tcpdump_radiotapdump('', 0)

        nrepeats = int(self.timeout)
        self.active_logs(nrepeats)
        print "DEBUG: "+str(time.time())+" START PINGING LOOP "
        if self.DIFF_PING:
            self.differential_ping()
        else:
            self.ping_all()

        print "DEBUG: "+str(time.time())+" state = " + state
        comment = exp()
        if self.non_blocking_experiment:
            #takes around 3 sec to transfer results properly for iperf3 RA tcp
            print '\nDEBUG: Sleep for ' + str(timeout + 5.0) + ' seconds as ' + comment + ' runs '+ str(self.experiment_counter) +'\n'
            time.sleep(timeout + 5.0)

        self.kill_all(1)
        self.transfer_logs(self.run_number, comment)

        #hack to start udp servers for next round
        self.start_servers()
        return

    def run_fast_experiment(self, exp, exp_name):

        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run "+ exp_name + " " + str(self.experiment_counter)
        self.experiment_name = exp_name #same as comment
        state = exp_name
        timeout = self.timeout
        self.get_folder_name_from_server()

        if self.tcpdump == 1:
            self.tcpdump_radiotapdump('', 0)

        nrepeats = int(self.timeout)
        self.active_logs(nrepeats)
        print "DEBUG: "+str(time.time())+" START PINGING LOOP "
        if self.DIFF_PING:
            self.differential_ping()
        else:
            self.ping_all()

        print "DEBUG: "+str(time.time())+" state = " + state
        comment = exp()
        if self.non_blocking_experiment:
            #takes around 3 sec to transfer results properly for iperf3 RA tcp
            print '\nDEBUG: Sleep for ' + str(timeout) + ' seconds as ' + comment + ' runs '+ str(self.experiment_counter) +'\n'
            time.sleep(timeout)

        self.kill_all()
        self.transfer_logs(self.run_number, comment)

        #don't kill the servers
        return

    def parse_probe(self, filename):
        fread = open(filename, 'r')
        capacity = defaultdict(list)
        lines = [line.rstrip('\n') for line in fread]
        if len(lines) == 0:
            print "no data "+ filename
            return capacity
        # router
        elif len(lines) == 1:
            router_data = lines[0].split('\x1b[2K\r')
            if len(router_data) > 0:
                for each_line in router_data[:-1]:
                    data = each_line.split()
                    if len(data) > 0:
                        if data[0] == 'Upload':
                            direction = 'up'
                            value = data[4]
                            train_num = data[3].rstrip(':')
                        elif data[0] == 'Download':
                            direction = 'dw'
                            value = data[4]
                            train_num = data[3].rstrip(':')
                        capacity[direction].append(float(value))
                        capacity['num_'+direction].append(train_num)
                lines = router_data
        # normal
        else:
            for line in lines[:-1]:
                data = line.split()
                direction = data[0]
                value = data[2]
                train_num = data[1].rstrip(':')
                capacity[direction].append(float(value))
                capacity['num_'+direction].append(train_num)
        if len(lines[-1].split(', ')) == 4:
            dstip, timestamp, capup, capdw = lines[-1].split(', ')
            capacity['num_up'].append('final')
            capacity['num_dw'].append('final')
            capacity['up'].append(float(capup))
            capacity['dw'].append(float(capdw))
            capacity['timestamp'] = timestamp
            capacity['dstip'] = dstip
            return capacity
        print 'Error in reading '+filename
        return capacity

    def parse_udpprobe_output(self, filename):
        #p = MyParser()
        df = self.parse_probe(filename)
        if len(df) > 0:
            return df['up'][10], df['dw'][10]
        return np.nan, np.nan

    def get_udpprobe_rate(self, x=1):
        comment = 'udp_probe'
        self.experiment_name = comment          #same as comment
        self.get_folder_name_from_server()
        if self.tcpdump == 1:
            self.tcpdump_radiotapdump('', 0)
        # set experiment suffix to none for blocking udpprober
        self.experiment_suffix = ''
        print "DONE ", self.probe_udp_AR()
        print "DONE ", self.probe_udp_AS()
        self.start_shaperprobe_udp_servers()
        print "DONE ", self.probe_udp_RS()
        time.sleep(15)
        # as RS probe is non blocking so sleep for 15 sec
        # if non blocking, set it back to bg process
        if self.non_blocking_experiment:
            self.experiment_suffix = ' &'
        self.kill_all(1)
        self.transfer_logs(self.run_number, comment)
        self.start_servers()
        #self.start_iperf3_servers()
        #if self.udp == 1:
        #    self.start_shaperprobe_udp_servers()
        #TODO read udp probe
        probe_path = '/tmp/data/'+self.unique_id + '/' +self.run_number+'_'+comment+'/'
        self.probe_rate['e2e'] = self.parse_udpprobe_output(probe_path + 'probe_AS_A.log')
        self.probe_rate['home'] = self.parse_udpprobe_output(probe_path + 'probe_AR_A.log')
        self.probe_rate['access'] = self.parse_udpprobe_output(probe_path + 'probe_RS_R.log')
        print "DEBUG: "+str(time.time())+": UDP probe (up, dw) home, access, e2e: ", self.probe_rate

        fout = open(probe_path + 'udp_probe.log', w)
        fout.write(self.probe_rate)
        fout.close()

        if x!= -1:
            self.set_udp_rate_mbit(float(self.probe_rate['access'][x])/1000, float(self.probe_rate['home'][x])/1000)

        return


    def no_traffic(self, timeout=0):
        if timeout == 0:
            timeout = self.timeout
        if not self.non_blocking_experiment:
            time.sleep(timeout)
        return 'no_tra'

    # iperf tcp
    def iperf_tcp(self, tx, rx, timeout, parallel, reverse=0):

        tx.command({'CMD':'killall iperf'})
        #rx.command({'CMD':'iperf -s -p '+ const.IPERF_TCP_PORT+' >> /tmp/browserlab/iperf_tcp_server_'+rx.name+'.log &'})
        #time.sleep()
        print str(time.time()) + " TCP DEBUG: start "+tx.name + rx.name
        recv_ip = rx.ip
        if tx.name == 'S' and rx.name == 'R':
            recv_ip = const.ROUTER_ADDRESS_GLOBAL

        cmd = 'iperf -c ' + recv_ip + ' -t '+str(timeout)+' -p '+const.IPERF_TCP_PORT
        if reverse:
            cmd = cmd + ' -r '                      #do a bidirectional test individually

        if parallel:
            cmd = cmd + ' -P '+str(self.num_parallel_streams)

        if tx.name == 'S':
            cmd = cmd + ' >> '+const.TMP_BROWSERLAB_PATH+'iperf_tcp_'+tx.name+rx.name+'_'+tx.name+'.log'+self.experiment_suffix
        else:
            cmd = cmd + ' >> /tmp/browserlab/iperf_tcp_'+tx.name+rx.name+'_'+tx.name+'.log'+self.experiment_suffix

        tx.command({'CMD': cmd, 'BLK':self.blk})
        if reverse:
            # if reverse it needs double the time for both way measurement
            time.sleep(timeout+0.2)
        print str(time.time()) + " TCP DEBUG: stop "+tx.name + rx.name

        return tx.name+rx.name + '_tcp'

    def iperf_udp(self, tx, rx, timeout, rate_mbit, reverse=0):
        #USE 100 mbit for wireless and limit for anything else
        #rx.command({'CMD': 'iperf -s -u -f k -y C >> /tmp/browserlab/iperf_udp_'+tx.name+rx.name+'_'+rx.name+'.log &'})

        tx.command({'CMD':'killall iperf'})
        print str(time.time()) + " UDP DEBUG: start "+tx.name + rx.name

        recv_ip = rx.ip
        if tx.name == 'S' and rx.name == 'R':
            recv_ip = const.ROUTER_ADDRESS_GLOBAL

        cmd = 'iperf -c ' + recv_ip + ' -u -b ' + rate_mbit + 'm -t '+str(timeout)+ ' -p '+const.IPERF_UDP_PORT
        if reverse:
            cmd = cmd + ' -r '                  #do a bidirectional test individually

        if tx.name == 'S':
            cmd = cmd + ' >> '+const.TMP_BROWSERLAB_PATH+'iperf_udp_'+tx.name+rx.name+'_'+tx.name+'.log'+self.experiment_suffix
        else:
            cmd = cmd + ' >> /tmp/browserlab/iperf_udp_'+tx.name+rx.name+'_'+tx.name+'.log'+self.experiment_suffix

        tx.command({'CMD': cmd, 'BLK':self.blk})
        if reverse:
            # if reverse it needs double the time for both way measurement
            time.sleep(timeout+0.2)
        print str(time.time()) + " UDP DEBUG: stop "+tx.name + rx.name

        return tx.name+rx.name + '_udp'

    def iperf3(self, tx, rx, link, timeout, reverse, proto='tcp', rate_mbit='100'):
        cmd = 'iperf3 -c '+rx.ip+' -p '+const.PERF_PORT
        if self.use_iperf_timeout:
            cmd = cmd +' -t '+str(timeout)+' -J -Z '
        else:
            cmd = cmd +' -n '+self.num_bits_to_send+' -J -Z '        #where timeout is number of bytes instead
        if reverse:
            cmd = cmd + ' -R '
        if proto != 'tcp':
            cmd = cmd + ' -u -b '+rate_mbit +'m'
        if self.parallel:
            cmd = cmd + ' -P '+str(self.num_parallel_streams)
        if self.use_window_size:
            cmd = cmd + ' -w '+self.window_size
        if self.use_omit_n_sec:
            cmd = cmd + ' -O '+self.omit_n_sec

        if tx.name == 'S':
            tx.command({'CMD': cmd + ' > '+const.TMP_BROWSERLAB_PATH+'iperf3_'+proto+'_'+link+'_'+tx.name+'.log'+self.experiment_suffix, 'BLK':self.blk})
        else:
            tx.command({'CMD': cmd + ' > /tmp/browserlab/iperf3_'+proto+'_'+link+'_'+tx.name+'.log'+self.experiment_suffix, 'BLK':self.blk})

        #if self.non_blocking_experiment:
        #    time.sleep(timeout+1.0)
        print "DEBUG: " + tx.name+ " " + str(time.time()) + " DONE: " + cmd + ' > /tmp/browserlab/iperf3_'+proto+'_'+link+'_'+tx.name+'.log'+self.experiment_suffix

        return link + '_' + proto

    def netperf_tcp(self, tx, rx, timeout, parallel=0, reverse=0):
        cmd = 'netperf -P 0 -f k -c -C -l ' + str(timeout) + ' -H ' + rx.ip + ' -p '+ const.NETPERF_PORT
        if reverse:
            proto = 'TCP_MAERTS'
            linkname = rx.name + tx.name
        else:
            proto = 'TCP_STREAM'
            linkname = tx.name + rx.name
        cmd += ' -t ' + proto
        logfile = ' > /tmp/browserlab/netperf_'+ linkname +'_'+tx.name+'.log'

        if parallel:
            logfile2 = ' > /tmp/browserlab/netperf_'+ linkname +'_'+tx.name
            cmd = 'for num in {1..'+str(self.num_parallel_streams)+'}; do echo "netperf $num";'+cmd + logfile2 +'$(num).log & done'
        else:
            cmd += logfile+self.experiment_suffix

        tx.command({'CMD': cmd})
        print "DEBUG: " + tx.name+ " " + str(time.time()) + " DONE: " + cmd
        return linkname + '_tcp'

    def probe_udp(self, tx, rx):
        cmd = 'udpprober -s ' + rx.ip + ' >> /tmp/browserlab/probe_'+ tx.name+rx.name+'_'+tx.name+'.log'+self.experiment_suffix
        tx.command({'CMD': cmd})
        #TODO hack: add sleep function here itself
        time.sleep(15)
        print "DEBUG: " + tx.name+ " " + str(time.time()) + " DONE: " + cmd
        return tx.name+rx.name+'_pro'

    def netperf_udp(self, tx, rx, timeout):
        cmd = 'netperf -t UDP_MAERTS -P 0 -f k -c -C -l ' + str(timeout) + ' -H ' + rx.ip + ' -p '+ const.NETPERF_PORT + ' > /tmp/browserlab/netperf_'+ tx.name + rx.name +'_'+tx.name+'.log'+self.experiment_suffix
        tx.command({'CMD': cmd})
        print "DEBUG: " + tx.name+ " " + str(time.time()) + " DONE: " + cmd
        return tx.name+rx.name + '_udp'

    #TCP
    def iperf_tcp_up_AR(self):
        return self.iperf_tcp(self.A, self.R, self.timeout, self.parallel, const.USE_IPERF_REV)

    def iperf3_tcp_up_AR(self):
        return self.iperf3(self.A, self.R, 'AR', self.timeout, 0, 'tcp', 0)

    def iperf3_tcp_up_AB(self):
        return self.iperf3(self.A, self.B, 'AB', self.timeout, 0, 'tcp', 0)

    def iperf3_tcp_up_BR(self):
        return self.iperf3(self.B, self.R, 'BR', self.timeout, 0, 'tcp', 0)

    def iperf3_tcp_dw_RB(self):
        return self.iperf3(self.B, self.R, 'RB', self.timeout, 1, 'tcp', 0)

    def iperf3_tcp_dw_BA(self):
        return self.iperf3(self.A, self.B, 'BA', self.timeout, 1, 'tcp', 0)

    def iperf3_tcp_up_BS(self):
        return self.iperf3(self.B, self.S, 'BS', self.timeout, 0, 'tcp', 0)

    def iperf3_tcp_dw_SB(self):
        return self.iperf3(self.B, self.S, 'SB', self.timeout, 1, 'tcp', 0)

    def netperf_tcp_up_AR(self):
        return self.netperf_tcp(self.A, self.R, self.timeout, self.parallel, 0)

    def iperf_tcp_up_RS(self):
        return self.iperf_tcp(self.R, self.S, self.timeout, self.parallel, const.USE_IPERF_REV)

    def iperf3_tcp_up_RS(self):
        return self.iperf3(self.R, self.S, 'RS', self.timeout, 0, 'tcp', 0)

    def netperf_tcp_up_RS(self):
        return self.netperf_tcp(self.R, self.S, self.timeout, self.parallel, 0)

    def iperf_tcp_up_AS(self):
        return self.iperf_tcp(self.A, self.S, self.timeout, self.parallel, const.USE_IPERF_REV)

    def iperf3_tcp_up_AS(self):
        return self.iperf3(self.A, self.S, 'AS', self.timeout, 0, 'tcp', 0)

    def netperf_tcp_up_AS(self):
        return self.netperf_tcp(self.A, self.S, self.timeout, self.parallel, 0)

    def iperf_tcp_dw_RA(self):
        return self.iperf_tcp(self.R, self.A, self.timeout, self.parallel, const.USE_IPERF_REV)

    def iperf3_tcp_dw_RA(self):
        return self.iperf3(self.A, self.R, 'RA', self.timeout, 1, 'tcp', 0)

    def netperf_tcp_dw_RA(self):
        return self.netperf_tcp(self.A, self.R, self.timeout, self.parallel, 1)

    def iperf_tcp_dw_SR(self):
        return self.iperf_tcp(self.S, self.R, self.timeout, self.parallel, const.USE_IPERF_REV)

    def iperf3_tcp_dw_SR(self):
        return self.iperf3(self.R, self.S, 'SR', self.timeout, 1, 'tcp', 0)

    def iperf3_tcp_dw_SR2(self):
        return self.iperf3(self.S, self.R, 'SR', self.timeout, 0, 'tcp', 0)

    def netperf_tcp_dw_SR(self):
        return self.netperf_tcp(self.R, self.S, self.timeout, self.parallel, 1)

    def iperf_tcp_dw_SA(self):
        return self.iperf_tcp(self.S, self.A, self.timeout, self.parallel, const.USE_IPERF_REV)

    def iperf3_tcp_dw_SA(self):
        return self.iperf3(self.A, self.S, 'SA', self.timeout, 1, 'tcp', 0)

    def netperf_tcp_dw_SA(self):
        return self.netperf_tcp(self.A, self.S, self.timeout, self.parallel, 1)

    #UDP
    def netperf_udp_up_AR(self):
        return self.netperf_udp(self.A, self.R, self.timeout)

    def netperf_udp_up_RS(self):
        return self.netperf_udp(self.R, self.S, self.timeout)

    def netperf_udp_up_AS(self):
        return self.netperf_udp(self.A, self.S, self.timeout)

    def netperf_udp_dw_RA(self):
        return self.netperf_udp(self.R, self.A, self.timeout)

    def netperf_udp_dw_SR(self):
        return self.netperf_udp(self.S, self.R, self.timeout)

    def netperf_udp_dw_SA(self):
        return self.netperf_udp(self.S, self.A, self.timeout)

    def probe_udp_AR(self):
        return self.probe_udp(self.A, self.R)

    def probe_udp_RS(self):
        return self.probe_udp(self.R, self.S)

    def probe_udp_AS(self):
        return self.probe_udp(self.A, self.S)

    def iperf_udp_up_AR(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_home
            proto='udp'
        self.iperf_udp(self.A, self.R, self.timeout, rate_mbit, const.USE_IPERF_REV)
        return 'AR_'+proto

    def iperf3_udp_up_AR(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_home
            proto='udp'
        return self.iperf3(self.A, self.R, 'AR', self.timeout, 0, proto, rate_mbit)

    def iperf_udp_up_RS(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_access
            proto='udp'
        self.iperf_udp(self.R, self.S, self.timeout, rate_mbit)
        return 'RS_'+proto

    def iperf3_udp_up_RS(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_access
            proto='udp'
        return self.iperf3(self.R, self.S, 'RS', self.timeout, 0, proto, rate_mbit)

    def iperf_udp_up_AS(self):
        if float(self.rate_access) > float(self.rate_home):
            rate_mbit = self.rate_home
        else:
            rate_mbit = self.rate_access
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            proto='udp'
        self.iperf_udp(self.A, self.S, self.timeout, rate_mbit)
        return 'AS_' + proto

    def iperf3_udp_up_AS(self):
        if float(self.rate_access) > float(self.rate_home):
            rate_mbit = self.rate_home
        else:
            rate_mbit = self.rate_access
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            proto='udp'
        return self.iperf3(self.A, self.S, 'AS', self.timeout, 0, proto, rate_mbit)

    def iperf_udp_dw_RA(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_home
            proto='udp'
        self.iperf_udp(self.R, self.A, self.timeout, rate_mbit)
        return 'RA_'+proto

    def iperf3_udp_dw_RA(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_home
            proto='udp'
        return self.iperf3(self.A, self.R, 'RA', self.timeout, 1, proto, rate_mbit)

    def iperf_udp_dw_SR(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_access
            proto='udp'
        self.iperf_udp(self.S, self.R, self.timeout, rate_mbit)
        return 'SR_' + proto

    def iperf3_udp_dw_SR(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_access
            proto='udp'
        return self.iperf3(self.R, self.S, 'SR', self.timeout, 1, proto, rate_mbit)

    def iperf_udp_dw_SA(self):
        if float(self.rate_access) > float(self.rate_home):
            rate_mbit = self.rate_home
        else:
            rate_mbit = self.rate_access
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            proto='udp'
        self.iperf_udp(self.S, self.A, self.timeout, rate_mbit)
        return 'SA_' + proto

    def iperf3_udp_dw_SA(self):
        if float(self.rate_access) > float(self.rate_home):
            rate_mbit = self.rate_home
        else:
            rate_mbit = self.rate_access
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            proto='udp'
        return self.iperf3(self.A, self.S, 'SA', self.timeout, 1, proto, rate_mbit)

    # fabprobe doesn't really work
    def fabprobe_SR(self):
        self.S.command({'CMD': 'time fabprobe_snd -d ' + const.ROUTER_ADDRESS_GLOBAL + ' > /tmp/browserlab/fabprobe_SR.log', 'BLK':self.blk})
        return 'SR_fab'
