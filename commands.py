from __future__ import division
from datetime import datetime
from random import randint

import time
import socket
import os
import paramiko
import threading
import subprocess
import shlex
import subprocess
import struct
import fcntl

from constants import *


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


def logcmd(cmd, name):
    if not os.path.exists('/tmp/browserlab/'):
        os.mkdir('/tmp/browserlab/')
    fileout = open('/tmp/browserlab/A_logcmd.log', 'a+w')
    fileout.write(name + ': ' + str(time.time()) +': '+ cmd + '\n')
    print 'DEBUG: '+ name + ': ' + str(time.time()) +': '+ cmd
    fileout.close()
    return


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
        if not ('TIMEOUT' in cmd):
            if 'STDOUT' in cmd:
                outfile = open(cmd['STDOUT'], 'a+w')
            else:
                outfile = None
            #use subprocess for immediate command
            p = subprocess.call(cmd['CMD'], stdout = outfile, shell = True)
        else:
            Command(cmd['CMD']).run(cmd['TIMEOUT'])
        logcmd(str(cmd), self.name)
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
            msg = str(cmd)  #remember to eval and check for flags on other end (START, TIMEOUT, CMD, SUDO(?))
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
    def __init__(self):
        self.A = Client(CLIENT_ADDRESS)
        self.R = Router(ROUTER_ADDRESS_LOCAL, ROUTER_USER, ROUTER_PASS)
        self.S = Server(SERVER_ADDRESS)
        self.device_list = [self.A, self.R, self.S]
        self.run_number = 0
        self.unique_id = self.get_mac_address()
        self.create_monitor_interface()

    def get_mac_address(self, ifname=CLIENT_WIRELESS_INTERFACE_NAME):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1].replace(':','')

    def get_folder_name_from_server(self):
        serv, run_number, pid = self.S.command({'CMD':'echo "create folder name"', 'START':1})
        self.run_number = run_number
        print 'DEBUG: run_number '+run_number
        return 0

    def create_monitor_interface(self):
        self.A.command({'CMD': 'iw dev '+ CLIENT_WIRELESS_INTERFACE_NAME +' interface add mon0 type monitor flags none'})
        self.R.command({'CMD': 'iw dev '+ ROUTER_WIRELESS_INTERFACE_NAME +' interface add mon0 type monitor flags none'})
        return 0

    def ifup_monitor_interface(self):
        self.A.command({'CMD': 'ifconfig mon0 up'})
        self.R.command({'CMD': 'ifconfig mon0 up'})
        return 0

    def radiotap_dump(self):
        self.ifup_monitor_interface()
        self.A.command({'CMD':'tcpdump -i mon0 -s 0 -p -U -w /tmp/browserlab/A_radiotap.pcap -G ' + str(experiment_timeout) + ' &'})
        self.R.command({'CMD':'tcpdump -i mon0 -s 0 -p -U -w /tmp/browserlab/R_radiotap.pcap -G ' + str(experiment_timeout)})

    def ping_all(self):
        self.S.command({'CMD':'fping '+ROUTER_ADDRESS_GLOBAL+' -p 100 -c '+ str(experiment_timeout * 10) + ' -r 1 -A >> /tmp/browserlab/fping_S.log &'})

        self.A.command({'CMD':'fping '+ROUTER_ADDRESS_LOCAL+' '+ SERVER_ADDRESS +' -p 100 -c '+ str(experiment_timeout * 10) + ' -r 1 -A >> /tmp/browserlab/fping_A.log &'})
        #self.R.command({'CMD':'fping '+CLIENT_ADDRESS+' '+ SERVER_ADDRESS +' -p 100 -l -r 1 -A >> /tmp/browserlab/fping_R.log &'})
        self.R.command({'CMD':'fping '+CLIENT_ADDRESS+' '+ SERVER_ADDRESS +' -p 100 -c '+ str(experiment_timeout * 10) + ' -r 1 -A >> /tmp/browserlab/fping_R.log &'})
        return

    def tcpdump_all(self):
        #weird bug with R.command(tcpdump) -> doesn't work with &
        self.S.command({'CMD':'tcpdump -s 100 -i eth0 -w /tmp/browserlab/S.pcap -G '+str(experiment_timeout)+' &'})
        self.A.command({'CMD':'tcpdump -s 100 -i '+ CLIENT_WIRELESS_INTERFACE_NAME +' -w /tmp/browserlab/A.pcap -G '+str(experiment_timeout)+' &'})
        self.R.command({'CMD':'tcpdump -s 100 -i '+ ROUTER_WIRELESS_INTERFACE_NAME +' -w /tmp/browserlab/R.pcap -G '+str(experiment_timeout)})
        return

    def process_log(self):
        self.S.command({'CMD':'sleep 5; top -b -n1 > /tmp/browserlab/S_process.log'})
        self.R.command({'CMD':'sleep 5; top -b -n1 > /tmp/browserlab/R_process.log'})
        self.A.command({'CMD':'sleep 5; top -b -n1 > /tmp/browserlab/A_process.log'})

        self.R.command({'CMD':'ifconfig > /tmp/browserlab/R_ifconfig.log'})
        return

    def kill_all(self):
        self.S.command({'CMD':'killall fping'}) #should be done with pid instead
        self.S.command({'CMD':'killall tcpdump'})
        self.S.command({'CMD':'killall iperf'})

        self.A.command({'CMD':'killall fping'}) #should be done with pid instead
        self.A.command({'CMD':'killall tcpdump'})
        self.A.command({'CMD':'killall iperf'})

        self.R.command({'CMD':'killall fping'}) #should be done with pid instead
        self.R.command({'CMD':'killall tcpdump'})
        self.R.command({'CMD':'killall iperf'})
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

        # TODO ftp upload /tmp/browserlab/run_number to server?
        self.S.command({'CMD': 'chown -R browserlab.browserlab /home/browserlab/'+self.unique_id+'/'+run_number+'_'+comment})
        self.S.command({'CMD': 'chmod -R 777 /home/browserlab/'+self.unique_id+'/'+run_number+'_'+comment})
        self.A.command({'CMD': 'sshpass -p passw0rd scp -o StrictHostKeyChecking=no -r /tmp/browserlab/'+run_number+'_'+comment+' browserlab@riverside.noise.gatech.edu:'+self.unique_id})

        return

    def run_experiment(self, exp):
        self.get_folder_name_from_server()
        self.tcpdump_all()
        self.radiotap_dump()
        self.ping_all()
        comment = exp()
        self.process_log()
        sleep_time = experiment_timeout + 2
        print '\nDEBUG: Sleep for ' + str(sleep_time) + ' seconds as experiment ' + comment + ' runs'
        time.sleep(sleep_time)
        self.kill_all()
        self.transfer_logs(self.run_number, comment)
        return

    def run_passive(self):
        comment = 'calibrate'
        self.get_folder_name_from_server()
        self.tcpdump_all()
        self.radiotap_dump()
        self.process_log()
        sleep_time = calibrate_timeout
        print '\nDEBUG: Sleep for ' + str(sleep_time) + ' seconds as experiment ' + comment + ' runs'
        time.sleep(sleep_time)
        self.kill_all()
        self.transfer_logs(self.run_number, comment)
        return


    # EXPERIMENTS
    # passed as args into run_experiment()
    def no_traffic(self):
        return 'no_tra'

    def iperf_tcp_up_AR(self):
        self.R.command({'CMD':'iperf -s -y C >> /tmp/browserlab/iperf_AR_R.log &'})
        self.A.command({'CMD':'iperf -c ' + ROUTER_ADDRESS_LOCAL + ' -y C -i 0.5 >> /tmp/browserlab/iperf_AR_A.log &'})
        return 'AR_tcp'

    def iperf_tcp_dw_RA(self):
        self.A.command({'CMD':'iperf -s -y C >> /tmp/browserlab/iperf_RA_A.log &'})
        self.R.command({'CMD':'iperf -c ' + CLIENT_ADDRESS + ' -y C -i 0.5 >> /tmp/browserlab/iperf_RA_R.log &'})
        return 'RA_tcp'

    def iperf_tcp_up_RS(self):
        self.S.command({'CMD':'iperf -s -y C >> /tmp/browserlab/iperf_RS_S.log &'})
        self.R.command({'CMD':'iperf -c ' + SERVER_ADDRESS + ' -y C -i 0.5 >> /tmp/browserlab/iperf_RS_R.log &'})
        return 'RS_tcp'

    def iperf_tcp_dw_SR(self):
        self.R.command({'CMD':'iperf -s -y C >> /tmp/browserlab/iperf_SR_R.log &'})
        self.S.command({'CMD':'iperf -c ' + ROUTER_ADDRESS_GLOBAL + ' -y C -i 0.5 >> /tmp/browserlab/iperf_SR_S.log &'})
        return 'SR_tcp'

    def iperf_tcp_up_AS(self):
        self.S.command({'CMD':'iperf -s -y C >> /tmp/browserlab/iperf_AR_R.log &'})
        self.A.command({'CMD':'iperf -c ' + SERVER_ADDRESS + ' -y C -i 0.5 >> /tmp/browserlab/iperf_AR_A.log &'})
        return 'AS_tcp'

    def iperf_tcp_dw_SA(self):
        #NOTE this requires iperf reverse installed on client and server
        self.S.command({'CMD':'iperf -s -y C -i 0.5 -t 10 --reverse >> /tmp/browserlab/iperf_SA_S.log &'})
        self.A.command({'CMD':'iperf -c ' + SERVER_ADDRESS + ' -y C --reverse >> /tmp/browserlab/iperf_SA_A.log &'})
        return 'SA_tcp'

    # udpprobe gives both up and dw
    def probe_udp_AR(self):
        self.R.command({'CMD':'udpprobeserver >> /tmp/browserlab/probe_AR_R.log &'})
        self.A.command({'CMD':'udpprober -s ' + ROUTER_ADDRESS_LOCAL + ' >> /tmp/browserlab/probe_AR_A.log &'})
        return 'AR_udp'

    def probe_udp_RS(self):
        self.S.command({'CMD':'udpprobeserver >> /tmp/browserlab/probe_RS_S.log &'})
        self.R.command({'CMD':'udpprober -s ' + SERVER_ADDRESS + ' >> /tmp/browserlab/probe_RS_R.log &'})
        return 'RS_udp'

    def probe_udp_AS(self):
        self.S.command({'CMD':'udpprobeserver >> /tmp/browserlab/probe_AS_S.log &'})
        self.A.command({'CMD':'udpprober -s ' + SERVER_ADDRESS + ' >> /tmp/browserlab/probe_AS_A.log &'})
        return 'AS_udp'
