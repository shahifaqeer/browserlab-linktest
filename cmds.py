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
import sys
import traceback

import const


CONTROL_PORT = const.CONTROL_PORT


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
        self.server = const.SERVER_ADDRESS
        self.client = const.CLIENT_ADDRESS
        self.router = const.ROUTER_ADDRESS_LOCAL
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
            y = const.ROUTER_ADDRESS_LOCAL+' '+ const.SERVER_ADDRESS
        else:
            y = ''
            for x in list_of_IPs:
                y = y + x + ' '
        self.command({'CMD':'fping '+ y +' -p 100 -c '+ str(self.timeout * 10) + ' -r 1 -A >> /tmp/browserlab/fping_A.log',
                   'TIMEOUT': self.timeout})
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
        self.port = const.CONTROL_PORT
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
                res, run_num, pid = response.split(',')
                while res == 1:
                    print 'Server is busy. Try again later.'
                s.close()
                if num_retries > 0:
                    run_num = "x"+run_num
                    msg = 'SCREWED ' + msg
                logcmd(msg, self.name)
                return res, run_num, pid
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
    time.sleep(self.timeout+2)
    kill_and_transfer(S,R,C, run_number, experiment_comment)
    return 0
"""


class Experiment:
    def __init__(self, measurement_name=None):
        self.A = Client(const.CLIENT_ADDRESS)
        self.R = Router(const.ROUTER_ADDRESS_LOCAL, const.ROUTER_USER, const.ROUTER_PASS)
        self.S = Server(const.SERVER_ADDRESS)
        self.check_connection()
        self.iface = self.get_default_interface()
        self.A.ip = self.get_ip_address(self.iface)
        self.device_list = [self.A, self.R, self.S]
        self.run_number = 0
        self.collect_calibrate = False
        self.experiment_counter = 0
        self.experiment_name = 'default'
        if measurement_name is not None:
            self.unique_id = self.get_mac_address() + '_' + measurement_name
        else:
            self.unique_id = self.get_mac_address()
        self.create_monitor_interface()

        self.set_test_timeout(const.EXPERIMENT_TIMEOUT)

        self.kill_all(1)  #kill tcpdump, iperf, netperf, fping on all
        self.clear_all(0) #clear /tmp/browserlab/* but don't close the connection to R

        self.tcp = const.COLLECT_tcp
        self.udp = const.COLLECT_udp
        self.blast = const.COLLECT_udp_blast
        self.tcpdump = const.COLLECT_tcpdump
        self.parallel = const.USE_PARALLEL_TCP
        self.use_iperf_timeout = const.USE_IPERF_TIMEOUT
        self.num_bits_to_send = const.NUM_BITS_TO_SEND

        if self.tcp == 1:
            self.start_netperf_servers()
        if self.udp == 1:
            self.start_iperf_udp_servers()
            self.start_shaperprobe_udp_servers()
        self.set_udp_rate_mbit(const.INIT_ACCESS_RATE, const.INIT_HOME_RATE, const.INIT_BLAST_RATE)

    def check_connection(self):
        cmd = {'CMD': 'echo "check port"'}
        if type(cmd) is dict:
            msg = str(cmd)  # remember to eval and check for flags on other end (START, TIMEOUT, CMD, SUDO(?))

        num_retries = 0
        port = const.CONTROL_PORT + num_retries % 5

        while num_retries<10:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((const.SERVER_ADDRESS, port))
                s.send(msg)
                response = s.recv(const.MSG_SIZE)
                print 'RECEIVED ', response
                res, run_num, pid = response.split(',')
                s.close()
                print "DEBUG: connection successful to "+const.SERVER_ADDRESS + ":" + str(port)
                CONTROL_PORT = port
                self.S.port = port
                return res, run_num, pid
            except Exception, error:
                print "DEBUG: Can't connect to "+str(const.SERVER_ADDRESS)+":"+str(port)+". \nRETRY "+str(num_retries+1)+" in 2 seconds."
                traceback.print_exc()
                num_retries += 1
                port = const.CONTROL_PORT + num_retries % 5    #try ports 12345 to 12349 twice each
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
        serv, run_number, pid = self.S.command({'CMD': 'echo "Bollocks!"', 'START': 1})
        self.run_number = run_number
        #print 'DEBUG: run_number ' + run_number
        return 0

    def create_monitor_interface(self):
        self.A.command({'CMD': 'iw dev '+ self.iface +'mon del'})
        self.R.command({'CMD': 'iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+'mon del'})
        self.A.command({'CMD': 'iw dev '+self.iface+' interface add '+self.iface+'mon type monitor flags none'})
        self.R.command({'CMD': 'iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' interface add '+const.ROUTER_WIRELESS_INTERFACE_NAME+'mon type monitor flags none'})
        self.ifup_monitor_interface()
        return

    def ifup_monitor_interface(self):
        self.A.command({'CMD': 'ifconfig '+self.iface+'mon up'})
        self.R.command({'CMD': 'ifconfig '+const.ROUTER_WIRELESS_INTERFACE_NAME+'mon up'})
        return

    def tcpdump_radiotapdump(self, state, timeout):
        # weird bug with R.command(tcpdump) -> doesn't work with &
        # also seems like timeout only kills the bash/sh -c process but not tcpdump itself - no wonder it doesn't work!
        if timeout:
            self.S.command({'CMD':'tcpdump -s 200 -i '+const.SERVER_INTERFACE_NAME+' -w '+const.TMP_BROWSERLAB_PATH+'tcpdump_S'+state+'.pcap', 'TIMEOUT': timeout})
        else:
            self.S.command({'CMD':'tcpdump -s 200 -i '+const.SERVER_INTERFACE_NAME+' -w '+const.TMP_BROWSERLAB_PATH+'tcpdump_S'+state+'.pcap &'})
        # dump at both incoming wireless and outgoing eth1 for complete picture

        if self.experiment_name[:2] == 'RS' or self.experiment_name[:2] == 'SR':
            router_interface_name = 'eth1'
        else:
            router_interface_name = const.ROUTER_WIRELESS_INTERFACE_NAME

        if router_interface_name[:4] == const.GENERIC_WIRELESS_INTERFACE_NAME:    #wlan
            # take only radiotap
            self.R.command({'CMD':'tcpdump -i '+const.ROUTER_WIRELESS_INTERFACE_NAME+'mon -s 200 -p -U -w /tmp/browserlab/radio_R'+state+'.pcap'})
            # need this for WTF
            #self.R.command({'CMD':'tcpdump -s 100 -i br-lan -w /tmp/browserlab/tcpdump_R'+state+'.pcap'})
            # need this for buffer timing check
            #self.R.command({'CMD':'tcpdump -s 100 -i eth1 -w /tmp/browserlab/tcpdump_eth1_R'+state+'.pcap'})
        else:
            self.R.command({'CMD':'tcpdump -s 100 -i '+router_interface_name+' -w /tmp/browserlab/tcpdump_R'+state+'.pcap'})

        if self.iface[:4] == const.GENERIC_WIRELESS_INTERFACE_NAME:
            # take only radiotap
            self.A.command({'CMD':'tcpdump -i '+self.iface+'mon -s 200 -p -U -w /tmp/browserlab/radio_A'+state+'.pcap &'})
        else:
            #self.A.command({'CMD':'tcpdump -s 100 -i '+const.CLIENT_WIRELESS_INTERFACE_NAME+' -w /tmp/browserlab/tcpdump_A'+state+'.pcap', 'TIMEOUT': timeout})
            self.A.command({'CMD':'tcpdump -s 100 -i '+self.iface+' -w /tmp/browserlab/tcpdump_A'+state+'.pcap &'})
        return

    def ping_all(self):
        timeout = 2 * self.timeout      # 20 sec
        # ALWAYS pass fping with & not to thread - thread seems to be blocking
        self.S.command({'CMD':'fping '+const.ROUTER_ADDRESS_GLOBAL+' -p 100 -c '+ str(timeout * 10) + ' -b ' + const.PING_SIZE + ' -r 1 -A > '+const.TMP_BROWSERLAB_PATH+'fping_S.log &'})
        self.R.command({'CMD':'fping '+self.A.ip+' '+ const.SERVER_ADDRESS +' ' + const.ROUTER_ADDRESS_PINGS + ' -p 100 -c '+ str(timeout * 10) + ' -b ' + const.PING_SIZE + ' -r 1 -A > /tmp/browserlab/fping_R.log &'})
        self.A.command({'CMD':'fping '+const.ROUTER_ADDRESS_LOCAL+' '+ const.SERVER_ADDRESS +' ' + const.ROUTER_ADDRESS_PINGS + ' -p 100 -c '+ str(timeout * 10) + ' -b ' + const.PING_SIZE +  ' -r 1 -A > /tmp/browserlab/fping_A.log &'})
        return

    def start_netperf_servers(self):
        self.S.command({'CMD': 'netserver'})
        self.R.command({'CMD': 'netserver'})
        self.A.command({'CMD': 'netserver'})
        return

    def start_iperf_udp_servers(self):
        if const.USE_IPERF3:
            for rx in [self.S, self.R, self.A]:
                rx.command({'CMD': 'iperf3 -s -p 5001 -J -D'})
        else:
            for rx in [self.R, self.A]:
                rx.command({'CMD': 'iperf -s -u -f k -y C >> /tmp/browserlab/iperf_udp_server_'+rx.name+'.log &'})
            self.S.command({'CMD': 'iperf -s -u -f k -y C >> '+const.TMP_BROWSERLAB_PATH+'iperf_udp_server_'+rx.name+'.log &'})
        return

    def start_shaperprobe_udp_servers(self):
        for rx in [self.R, self.A]:
            rx.command({'CMD': 'udpprobeserver >> /tmp/browserlab/probe_server_'+rx.name+'.log &'})
        self.S.command({'CMD': 'udpprobeserver >> '+const.TMP_BROWSERLAB_PATH+'probe_server_'+rx.name+'.log &'})
        return

    def convert_sar_to_log(self):
        for dev in [self.R, self.A]:
            dev.command({'CMD':'sar -f /tmp/browserlab/sar_' + dev.name + '.out > /tmp/browserlab/sar_' + dev.name + '.log;rm -rf /tmp/browserlab/sar_' + dev.name + '.out'})
        self.S.command({'CMD':'sar -f '+const.TMP_BROWSERLAB_PATH+'sar_' + dev.name + '.out > '+const.TMP_BROWSERLAB_PATH+'sar_' + dev.name + '.log;rm -rf '+const.TMP_BROWSERLAB_PATH+'sar_' + dev.name + '.out'})
        return

    def active_logs(self, nrepeats, delta_time=1):
        nrepeats = str(nrepeats)
        delta_time = str(delta_time)
        self.S.command({'CMD': 'nohup sar -o '+const.TMP_BROWSERLAB_PATH+'sar_S.out ' + delta_time + ' ' + nrepeats + ' >/dev/null 2>&1 &'})
        self.R.command({'CMD': 'sar -o /tmp/browserlab/sar_R.out ' + delta_time + ' ' + nrepeats + ' >/dev/null 2>&1 &'})
        self.A.command({'CMD': 'nohup sar -o /tmp/browserlab/sar_A.out ' + delta_time + ' ' + nrepeats + ' >/dev/null 2>&1 &'})

        self.S.command({'CMD':'for i in $(seq 1 1 '+nrepeats+');do\
        echo "$i: $(date)" >> '+const.TMP_BROWSERLAB_PATH+'ifconfig_S.log;\
        ifconfig  >> '+const.TMP_BROWSERLAB_PATH+'ifconfig_S.log;\
        sleep ' + delta_time + '; done &'})

        self.R.command({'CMD':'for i in $(seq 1 1 '+nrepeats+');do\
        echo "$i: $(date)" >> /tmp/browserlab/iw_R.log;\
        iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' survey dump >> /tmp/browserlab/iw_R.log;\
        iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iw_R.log;\
        sleep ' + delta_time + '; done &'})

        self.A.command({'CMD':'for i in $(seq 1 1 '+nrepeats+');do\
        echo "$i: $(date)" >> /tmp/browserlab/iw_A.log;\
        iw dev '+const.CLIENT_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iw_A.log;\
        sleep ' + delta_time + '; done &'})

        return

    def process_log(self, comment):
        poll_freq = 1
        ctr_len = str(int(self.timeout/poll_freq))

        for dev in [self.S, self.R, self.A]:
            #dev.command({'CMD':'for i in {1..'+ctr_len+'}; do top -b -n1 >> /tmp/browserlab/top_'+dev.name+'.log; sleep '+str(poll_freq)+'; done &'})
            dev.command({'CMD':'echo "$(date): ' + comment + '" >> /tmp/browserlab/top_'+dev.name+'.log;'})
            dev.command({'CMD':'top -b -n1 >> /tmp/browserlab/top_'+dev.name+'.log;'})
        return

    def interface_log(self, comment):
        poll_freq = 1
        ctr_len = str(int(self.timeout/poll_freq))

        #ifconfig (byte counters) for S
        #self.S.command({'CMD':'for i in {1..'+ctr_len+'}; do ifconfig >> /tmp/browserlab/ifconfig_'+self.S.name+'.log; sleep '+str(poll_freq)+'; done &'})
        self.S.command({'CMD':'echo "$(date): ' + comment + '" >> '+const.TMP_BROWSERLAB_PATH+'ifconfig_'+self.S.name+'.log;'})
        self.S.command({'CMD':'ifconfig >> '+const.TMP_BROWSERLAB_PATH+'ifconfig_'+self.S.name+'.log'})

        #iw dev (radiotap info) for wireless
        #self.R.command({'CMD':'for i in {1..'+ctr_len+'}; do iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iwdev_'+self.R.name+'.log; sleep '+str(poll_freq)+'; done &'})
        #self.A.command({'CMD':'for i in {1..'+ctr_len+'}; do iw dev '+self.iface+' station dump >> /tmp/browserlab/iwdev_'+self.A.name+'.log; sleep '+str(poll_freq)+'; done &'})
        self.R.command({'CMD':'echo "$(date): ' + comment + '" >> /tmp/browserlab/iwdev_'+self.R.name+'.log;'})
        self.R.command({'CMD':'iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' station dump >> /tmp/browserlab/iwdev_'+self.R.name+'.log'})
        self.A.command({'CMD':'echo "$(date): ' + comment + '" >> /tmp/browserlab/iwdev_'+self.A.name+'.log;'})
        self.A.command({'CMD':'iw dev '+self.iface+' station dump >> /tmp/browserlab/iwdev_'+self.A.name+'.log'})
        return

    def airtime_util_log(self, comment):
        poll_freq = 1
        ctr_len = str(int(self.timeout/poll_freq))
        if comment == 'during':
            self.R.command({'CMD':'for i in (seq 1 1 '+ctr_len+'); do iw dev '+const.ROUTER_WIRELESS_INTERFACE_NAME+' survey dump >> /tmp/browserlab/iwsurvey_'+self.R.name+'.log; sleep '+str(poll_freq)+'; done &'})
        return

    def kill_all(self, all_proc = 0):
        self.S.command({'CMD': 'killall tcpdump'})
        self.A.command({'CMD': 'killall tcpdump'})
        self.R.command({'CMD': 'killall tcpdump'})

        if all_proc:
            for node in [self.A, self.R, self.S]:
                node.command({'CMD': 'killall iperf'})
                node.command({'CMD': 'killall iperf3'})
                node.command({'CMD': 'killall netperf'})
        return

    def clear_all(self, close_R=0):
        self.S.command({'CMD': 'rm -rf '+const.TMP_BROWSERLAB_PATH+'*'})
        self.R.command({'CMD': 'rm -rf /tmp/browserlab/*'})
        self.A.command({'CMD': 'rm -rf /tmp/browserlab/*.log'})
        self.A.command({'CMD': 'rm -rf /tmp/browserlab/*.pcap'})
        if close_R:
            self.R.host.close()
        return

    def transfer_logs(self, run_number, comment):
        self.convert_sar_to_log()

        self.S.command({'CMD':'mkdir -p '+TMP_DATA_PATH+self.unique_id+'/'+run_number+'_'+comment})
        self.S.command({'CMD':'cp '+const.TMP_BROWSERLAB_PATH+'*.log '+const.TMP_DATA_PATH+self.unique_id+'/'+run_number+'_'+comment})
        self.S.command({'CMD':'cp '+const.TMP_BROWSERLAB_PATH+'*.pcap '+const.TMP_DATA_PATH+self.unique_id+'/'+run_number+'_'+comment})

        self.A.command({'CMD': 'mkdir -p /tmp/browserlab/'+run_number+'_'+comment}) # instead of time use blocking resource to sync properly
        self.A.command({'CMD':'cp /tmp/browserlab/*.log /tmp/browserlab/'+run_number+'_'+comment+'/'})
        self.A.command({'CMD':'cp /tmp/browserlab/*.pcap /tmp/browserlab/'+run_number+'_'+comment+'/'})

        self.A.command({'CMD':'sshpass -p '+ const.ROUTER_PASS +' scp -o StrictHostKeyChecking=no '+ const.ROUTER_USER + '@' + const.ROUTER_ADDRESS_LOCAL + ':/tmp/browserlab/* /tmp/browserlab/'+run_number+'_'+comment+'/'})

        self.R.command({'CMD':'rm -rf /tmp/browserlab/*.pcap'})
        self.R.command({'CMD':'rm -rf /tmp/browserlab/*.log'})
        self.A.command({'CMD':'rm -rf /tmp/browserlab/*.pcap'})
        self.A.command({'CMD':'rm -rf /tmp/browserlab/*.log'})
        self.S.command({'CMD':'rm -rf '+const.TMP_BROWSERLAB_PATH+'*.pcap'})
        self.S.command({'CMD':'rm -rf '+const.TMP_BROWSERLAB_PATH+'*.log'})

        #self.S.command({'CMD': 'chown -R browserlab:browserlab /home/browserlab/'+self.unique_id+'/'+run_number+'_'+comment})
        #self.S.command({'CMD': 'chmod -R 777 /home/browserlab/'+self.unique_id+'/'+run_number+'_'+comment})
        #self.A.command({'CMD': 'sshpass -p passw0rd scp -o StrictHostKeyChecking=no -r /tmp/browserlab/'+run_number+'_'+comment+' browserlab@' + const.SERVER_ADDRESS + ':'+self.unique_id})
        self.A.command({'CMD': 'mkdir -p /tmp/data/' + self.unique_id})
        self.A.command({'CMD': 'mv -f /tmp/browserlab/* /tmp/data/' + self.unique_id + '/'})

        return

    def transfer_all_later(self):
        #self.A.command({'CMD': 'sshpass -p passw0rd scp -o StrictHostKeyChecking=no -r /tmp/data/' +self.unique_id+ '/* browserlab@' + const.SERVER_ADDRESS + ':'+self.unique_id})
        self.A.command({'CMD': 'sshpass -p passw0rd scp -o StrictHostKeyChecking=no -r /tmp/data/' +self.unique_id+ ' '+const.DATA_SERVER_PATH})
        self.S.command({'CMD': 'sshpass -p passw0rd scp -o StrictHostKeyChecking=no -r '+const.TMP_DATA_PATH+self.unique_id+'/* '+const.DATA_SERVER_PATH+self.unique_id+'/'})
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


    def run_experiment(self, exp, exp_name):
        self.experiment_name = exp_name #same as comment

        self.get_folder_name_from_server()

        if self.tcpdump == 1:
            self.tcpdump_radiotapdump('', 0)

        nrepeats = 2 + int(self.timeout) + 2
        self.active_logs(nrepeats)

        state = 'before'
        print "DEBUG: "+str(time.time())+" state = " + state
        timeout=2
        time.sleep(timeout)
        print '\nDEBUG: Sleep for ' + str(timeout) + ' seconds as dump runs '+ str(self.experiment_counter) +'\n'

        self.ping_all()

        timeout = 2 * self.timeout        # 20 sec
        if exp_name == 'SR_fab':
            timeout = 4 * self.timeout    # 40 sec

        state = 'during'
        print "DEBUG: "+str(time.time())+" state = " + state
        comment = exp()
        print '\nDEBUG: Sleep for ' + str(timeout) + ' seconds as ' + comment + ' runs '+ str(self.experiment_counter) +'\n'
        time.sleep(timeout)

        state = 'after'
        print "DEBUG: "+str(time.time())+" state = " + state

        self.kill_all(1)
        self.transfer_logs(self.run_number, comment)

        #hack to start udp servers for next round
        if self.udp == 1:
            self.start_iperf_udp_servers()
            self.start_shaperprobe_udp_servers()

        return

    def run_calibrate(self):
        self.get_folder_name_from_server()
        self.passive('calibrate', const.CALIBRATE_TIMEOUT)
        self.transfer_logs(self.run_number, 'calibrate')
        return


    # EXPERIMENTS
    # passed as args into run_experiment()
    def no_traffic(self):
        return 'no_tra'

    def set_udp_rate_mbit(self, rate_access, rate_home=100, rate_blast=1000):
        self.rate_access = str(rate_access)
        self.rate_home = str(rate_home)
        self.rate_blast = str(rate_blast)
        return

    def set_test_timeout(self, timeout=const.EXPERIMENT_TIMEOUT):
        self.timeout = timeout
        return

    # iperf tcp
    def iperf_tcp_up_AR(self):
        self.R.command({'CMD': 'iperf -s -y C > /tmp/browserlab/iperf_AR_R.log &'})
        self.A.command({'CMD': 'iperf -c ' + const.ROUTER_ADDRESS_LOCAL + ' -y C -i 0.5 > /tmp/browserlab/iperf_AR_A.log &'})
        return 'AR_tcp'

    def iperf_tcp_dw_RA(self):
        self.A.command({'CMD': 'iperf -s -y C > /tmp/browserlab/iperf_RA_A.log &'})
        self.R.command({'CMD': 'iperf -c ' + self.A.ip + ' -y C -i 0.5 > /tmp/browserlab/iperf_RA_R.log &'})
        return 'RA_tcp'

    def iperf_tcp_up_RS(self):
        self.S.command({'CMD': 'iperf -s -y C > '+const.TMP_BROWSERLAB_PATH+'iperf_RS_S.log &'})
        self.R.command({'CMD': 'iperf -c ' + const.SERVER_ADDRESS + ' -y C -i 0.5 > /tmp/browserlab/iperf_RS_R.log &'})
        return 'RS_tcp'

    def iperf_tcp_dw_SR(self):
        self.R.command({'CMD': 'iperf -s -y C > /tmp/browserlab/iperf_SR_R.log &'})
        self.S.command({'CMD': 'iperf -c ' + const.ROUTER_ADDRESS_GLOBAL + ' -y C -i 0.5 > '+const.TMP_BROWSERLAB_PATH+'iperf_SR_S.log &'})
        return 'SR_tcp'

    def iperf_tcp_up_AS(self):
        self.S.command({'CMD': 'iperf -s -y C >> '+const.TMP_BROWSERLAB_PATH+'iperf_AS_S.log &'})
        self.A.command({'CMD': 'iperf -c ' + const.SERVER_ADDRESS + ' -y C -i 0.5 > /tmp/browserlab/iperf_AS_A.log &'})
        return 'AS_tcp'

    def iperf_tcp_dw_SA(self):
        #NOTE this requires iperf reverse installed on client and server
        self.S.command({'CMD': 'iperf -s -y C -i 0.5 -t 10 --reverse > '+const.TMP_BROWSERLAB_PATH+'iperf_SA_S.log &'})
        self.A.command({'CMD': 'iperf -c ' + const.SERVER_ADDRESS + ' -y C --reverse > /tmp/browserlab/iperf_SA_A.log &'})
        return 'SA_tcp'

    # netperf tcp
    def netperf_tcp_up_AR(self):
        # v2.4.5; default port 12865; reverse tcp stream RA
        #self.R.command({'CMD': 'netperf -t TCP_MAERTS -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + self.A.ip + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_AR_R.log &'})
        if const.USE_IPERF3:
            return self.iperf3(self.A, self.R, 'AR', self.timeout, 0, 'tcp', 0)
        else:
            self.A.command({'CMD': 'netperf -t TCP_STREAM -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + self.R.ip + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_AR_A.log &'})
        return 'AR_tcp'

    def netperf_tcp_up_RS(self):
        # reverse tcp stream RS
        if const.USE_IPERF3:
            return self.iperf3(self.R, self.S, 'RS', self.timeout, 0, 'tcp', 0)
        else:
            self.R.command({'CMD': 'netperf -t TCP_STREAM -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + const.SERVER_ADDRESS + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_RS_R.log &'})
        #self.S.command({'CMD': 'netperf -t TCP_MAERTS -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + const.ROUTER_ADDRESS_GLOBAL + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_RS_S.log &'})
        return 'RS_tcp'

    def netperf_tcp_up_AS(self):
        # reverse tcp stream AS
        if const.USE_IPERF3:
            return self.iperf3(self.A, self.S, 'AS', self.timeout, 0, 'tcp', 0)
        else:
            self.A.command({'CMD': 'netperf -t TCP_STREAM -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + const.SERVER_ADDRESS + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_AS_A.log &'})
        return 'AS_tcp'

    def netperf_tcp_dw_RA(self):
        # v2.4.5; default port 12865; tcp stream RA
        #self.R.command({'CMD': 'netperf -t TCP_STREAM -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + self.A.ip  + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_RA_R.log &'})
        if const.USE_IPERF3:
            return self.iperf3(self.A, self.R, 'RA', self.timeout, 1, 'tcp', 0)
        else:
            self.A.command({'CMD': 'netperf -t TCP_MAERTS -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + self.R.ip  + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_RA_A.log &'})
        return 'RA_tcp'

    def netperf_tcp_dw_SR(self):
        # reverse tcp stream RS
        if const.USE_IPERF3:
            return self.iperf3(self.R, self.S, 'SR', self.timeout, 1, 'tcp', 0)
        else:
            self.R.command({'CMD': 'netperf -t TCP_MAERTS -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + const.SERVER_ADDRESS + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_SR_R.log &'})
        #self.S.command({'CMD': 'netperf -t TCP_STREAM -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + const.ROUTER_ADDRESS_GLOBAL + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_SR_S.log &'})
        return 'SR_tcp'

    def netperf_tcp_dw_SA(self):
        # reverse tcp stream AS
        if const.USE_IPERF3:
            return self.iperf3(self.A, self.S, 'SA', self.timeout, 1, 'tcp', 0)
        else:
            self.A.command({'CMD': 'netperf -t TCP_MAERTS -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + const.SERVER_ADDRESS + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_SA_A.log &'})
        return 'SA_tcp'

    def netperf_tcp(self, tx, rx, rev=0):
        if tx.name == 'S' and rx.name == 'R':
            recv_ip = const.ROUTER_ADDRESS_GLOBAL
        else:
            recv_ip = rx.ip

        if rev:
            rx.command({'CMD': 'netperf -t TCP_MAERTS -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + tx.ip + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_'+tx.name+rx.name+'_'+rx.name+'.log &'})
        else:
            tx.command({'CMD': 'netperf -t TCP_STREAM -P 0 -f k -c -C -l '+str(self.timeout)+' -H ' + recv_ip + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_'+tx.name+rx.name+'_'+tx.name+'.log &'})

        return tx.name + rx.name + '_tcp'

    # netperf udp
    def netperf_udp_dw_SA(self):
        # reverse tcp stream AS
        self.S.command({'CMD': 'netperf -t UDP_STREAM -P 0 -f k -c -l 10 -H ' + self.A.ip + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_SA_S.log &'})
        return 'SA_udp'

    def netperf_udp_dw_SR(self):
        # reverse tcp stream RS
        self.S.command({'CMD': 'netperf -t UDP_STREAM -P 0 -f k -c -l 10 -H ' + const.ROUTER_ADDRESS_GLOBAL + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_SR_S.log &'})
        return 'SR_udp'

    def netperf_udp_dw_RA(self):
        # v2.4.5; default port 12865; tcp stream RA
        self.R.command({'CMD': 'netperf -t UDP_STREAM -P 0 -f k -c -l 10 -H ' + self.A.ip  + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_RA_R.log &'})
        return 'RA_udp'

    def netperf_udp_up_AR(self):
        # v2.4.5; default port 12865; tcp stream RA
        self.A.command({'CMD': 'netperf -t UDP_STREAM -P 0 -f k -c -l 10 -H ' + self.R.ip  + ' -- -P ' + const.PERF_PORT + ' > /tmp/browserlab/netperf_RA_R.log &'})
        return 'AR_udp'

    # udpprobe gives both up and dw
    def probe_udp_AR(self):
        self.A.command({'CMD': 'udpprober -s ' + self.R.ip + ' >> /tmp/browserlab/probe_AR_A.log &'})
        return 'AR_pro'

    def probe_udp_RS(self):
        self.R.command({'CMD': 'udpprober -s ' + self.S.ip + ' >> /tmp/browserlab/probe_RS_R.log &'})
        return 'RS_pro'

    def probe_udp_AS(self):
        self.A.command({'CMD': 'udpprober -s ' + self.S.ip + ' >> /tmp/browserlab/probe_AS_A.log &'})
        return 'AS_pro'

    # fabprobe doesn't really work
    def fabprobe_SR(self):
        self.S.command({'CMD': 'time fabprobe_snd -d ' + const.ROUTER_ADDRESS_GLOBAL + ' > /tmp/browserlab/fabprobe_SR.log'})
        return 'SR_fab'

    # iperf udp
    def iperf_udp(self, tx, rx, timeout, rate_mbit):
        #USE 100 mbit for wireless and limit for anything else
        #rx.command({'CMD': 'iperf -s -u -f k -y C >> /tmp/browserlab/iperf_udp_'+tx.name+rx.name+'_'+rx.name+'.log &'})

        print str(time.time()) + " UDP DEBUG: start "+tx.name + rx.name

        recv_ip = rx.ip
        if tx.name == 'S' and rx.name == 'R':
            recv_ip = const.ROUTER_ADDRESS_GLOBAL
            tx.command({'CMD': 'iperf -c ' + recv_ip + ' -u -b ' + rate_mbit + 'm -f k -y C -t '+str(timeout)+' >> '+const.TMP_BROWSERLAB_PATH+'iperf_udp_'+tx.name+rx.name+'_'+tx.name+'.log &'})
        else:
            tx.command({'CMD': 'iperf -c ' + recv_ip + ' -u -b ' + rate_mbit + 'm -f k -y C -t '+str(timeout)+' >> /tmp/browserlab/iperf_udp_'+tx.name+rx.name+'_'+tx.name+'.log &'})
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
            cmd = cmd + ' -P '+str(const.TCP_PARALLEL_STREAMS)

        if tx.name == 'S':
            tx.command({'CMD': cmd + ' > '+const.TMP_BROWSERLAB_PATH+'iperf3_'+proto+'_'+link+'_'+tx.name+'.log &'})
        else:
            tx.command({'CMD': cmd + ' > /tmp/browserlab/iperf3_'+proto+'_'+link+'_'+tx.name+'.log &'})

        time.sleep(timeout+0.2)
        print str(time.time()) + " DONE iperf3 DEBUG: " + cmd + ' > /tmp/browserlab/iperf3_'+proto+'_'+link+'_'+tx.name+'.log &'

        return link + '_' + proto

    def iperf_udp_up_AR(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_home
            proto='udp'
        if const.USE_IPERF3:
            return self.iperf3(self.A, self.R, 'AR', self.timeout, 0, proto, rate_mbit)
        else:
            self.iperf_udp(self.A, self.R, self.timeout, rate_mbit)
            return 'AR_'+proto

    def iperf_udp_dw_RA(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_home
            proto='udp'
        if const.USE_IPERF3:
            return self.iperf3(self.A, self.R, 'RA', self.timeout, 1, proto, rate_mbit)
        else:
            self.iperf_udp(self.R, self.A, self.timeout, rate_mbit)
            return 'RA_'+proto

    def iperf_udp_up_RS(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_access
            proto='udp'
        if const.USE_IPERF3:
            return self.iperf3(self.R, self.S, 'RS', self.timeout, 0, proto, rate_mbit)
        else:
            self.iperf_udp(self.R, self.S, self.timeout, rate_mbit)
            return 'RS_'+proto

    def iperf_udp_dw_SR(self):
        if self.blast:
            rate_mbit = self.rate_blast
            proto='bla'
        else:
            rate_mbit = self.rate_access
            proto='udp'
        if const.USE_IPERF3:
            return self.iperf3(self.R, self.S, 'SR', self.timeout, 1, proto, rate_mbit)
        else:
            self.iperf_udp(self.S, self.R, self.timeout, rate_mbit)
            return 'SR_' + proto

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
        if const.USE_IPERF3:
            return self.iperf3(self.A, self.S, 'AS', self.timeout, 0, proto, rate_mbit)
        else:
            self.iperf_udp(self.A, self.S, self.timeout, rate_mbit)
            return 'AS_' + proto

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
        if const.USE_IPERF3:
            return self.iperf3(self.A, self.S, 'SA', self.timeout, 1, proto, rate_mbit)
        else:
            self.iperf_udp(self.S, self.A, self.timeout, rate_mbit)
            return 'SA_' + proto

    # run experiments
    def run_udpprobe(self, exp, exp_name):
        self.exp_name = exp_name
        self.get_folder_name_from_server()

        nrepeats = 2 + int(self.timeout) + 2
        self.active_logs(nrepeats)

        state = 'before'
        print "DEBUG: "+str(time.time())+" state = " + state
        timeout=2
        time.sleep(timeout)
        print '\nDEBUG: Sleep for ' + str(timeout) + ' seconds as dump runs '+ str(self.experiment_counter) +'\n'

        state = 'during'
        print "DEBUG: "+str(time.time())+" state = " + state
        comment = exp()
        time.sleep(const.PROBE_TIMEOUT)

        print '\nDEBUG: Sleep for ' + str(const.PROBE_TIMEOUT) + ' seconds as ' + comment + ' runs '+ str(self.experiment_counter) +'\n'

        state = 'after'
        print "DEBUG: "+str(time.time())+" state = " + state

        self.kill_all(1)
        self.transfer_logs(self.run_number, comment)

        #hack to start udp servers for next round
        if self.udp == 1:
            self.start_iperf_udp_servers()
            self.start_shaperprobe_udp_servers()

        return
