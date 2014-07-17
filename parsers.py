from __future__ import division
import pandas as pd
import os, subprocess
import numpy as np
from collections import defaultdict


class MyParser:

    def __init__(self):
        """This is a parser for fping, ping, iperf, and probe"""
        print "You asked for a Parser!"

    # iperf
    def parse_iperf3(self, filename):
        data = defaultdict(int)
        df = pd.read_json(filename, typ='Series')
        data['num_streams'] = df['start']['test_start']['num_streams']
        data['remote_util'] = df['end']['cpu_utilization_percent']['remote_total']
        data['host_util'] = df['end']['cpu_utilization_percent']['host_total']
        data['proto'] = df['start']['test_start']['protocol']
        if data['proto'] == 'UDP':
            data['jitter_ms'] = df['end']['sum']['jitter_ms']
            data['lost_percent'] = df['end']['sum']['lost_percent']
            data['throughput'] = df['end']['sum']['bits_per_second']/1000
            data['interval'] = df['end']['sum']['seconds']
            data['bytes'] = df['end']['sum']['bytes']
        else:
            data['throughput'] = df['end']['sum_received']['bits_per_second']/1000
            data['throughput_sent'] = df['end']['sum_sent']['bits_per_second']/1000
            data['retransmits'] = df['end']['sum_sent']['retransmits']
            data['interval'] = df['end']['sum_received']['seconds']
            data['bytes'] = df['end']['sum_received']['bytes']
            data['bytes_sent'] = df['end']['sum_sent']['bytes']
        return pd.Series(data)

    def parse_iperf(self, filename, traff='tcp'):
        """input: iperf client log (assume -i 0.5)
        output: dataframe with last low as final report
        bandwidth in kilo bits per sec"""
        if traff=='tcp':
            df = pd.read_csv(filename, skipinitialspace=True,
                            names=['timestamp','srcip','sport', 'dstip',
                                    'dport', 'ignore', 'time', 'bytes',
                                    'bandwidth'])
            #df["datetime"] = df.timestamp.apply(lambda x: datetime(int(str(x)[:4]), int(str(x)[4:6]), int(str(x)[6:8]), int(str(x)[8:10]), int(str(x)[10:12]), int(str(x)[12:])))
            if "bandwidth" in df:
                df["bandwidth"] = df["bandwidth"]/1000  #kbps
            else:
                df["bandwidth"] = np.NaN
            #df = df.set_index('datetime')
            #df["include"] = [np.mod(x,21) for x in range(1,len(df)+1)]
            return df#[df["include"]==0]["bandwidth"]

        if traff=='udp':
            df = pd.read_csv(filename, skipinitialspace=True, names=['timestamp','srcip',
                            'sport', 'dstip', 'dport', 'process', 'time', 'bytes', 'bandwidth',
                            'jitter', 'lost_datagrams', 'total_datagrams', 'percentage_loss', 'out_of_order_datagrams'])
            if "bandwidth" in df:
                tp = df.iloc[1::2][['bandwidth', 'jitter', 'percentage_loss']]
                tp["bandwidth"] = tp["bandwidth"]/1000  #kbps
            else:
                tp = pd.DataFrame({'bandwidth':np.NaN, 'jitter':np.NaN, 'percentage_loss':np.NaN})
            return tp


    def parse_netperf(self, filename):
        #df = pd.read_csv(filename, names=['rxSockSize','txSockSize','msgSize', 'testTime', 'throughput', 'localUtil', 'remoteUtil', 'localService', 'remoteDemand'])
        keys = ['rxSockSize','txSockSize','msgSize', 'testTime', 'throughput',
                    'localUtil', 'remoteUtil', 'localService', 'remoteDemand']
        # units: bytes|bytes|bytes|secs.|10^3bits/s|% S|% U|us/KB|us/KB
        line = open(filename, 'r').readline()
        vals = line.strip('\n').split()
        if len(vals)>0:
            netperf = dict(zip(keys, vals))
        else:
            print "No netperf data in "+filename
            netperf = np.NaN
        return netperf

    def get_iperf_bw(self, filename):
        """input iperf client log; output final bw value in kbps"""
        #last line has avg values
        for line in open(filename, 'r'):
            pass
        bw = line.split(',')[-1].strip()
        return int(bw)/1000  # bw in kbps

    # probe
    #probe parser
    #probe parser
    def parse_probe(self, filename):
        """
        input: probe client file with bw for each train
        output: dataframe with dstip, timestamp, capup, capdw, series num for each train

        load udp probe log csv and returns pandas dataframe
        Dataframe fields: timestamp, srcip, sport, dstip, dport, ignore,
        time, bytes, bandwidth
        Parameter: log file (location/name)"""

        fread = open(filename, 'r')
        capacity = defaultdict(list)
        lines = [line.rstrip('\n') for line in fread]
        if len(lines) == 0:
            print "no data "+ filename
            return pd.DataFrame()
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
            return pd.DataFrame(capacity)
        print 'Error in reading '+filename
        return pd.DataFrame()

    def get_probe_bw(self, filename):
        """input: client probe log
        output: capup and capdw"""
        fread = open(filename, 'r')
        capup = []
        capdw = []
        lines = [line.rstrip('\n') for line in fread]
        data = lines[-1].split(', ')
        capup = float(data[2])
        capdw = float(data[3])
        # last line has avg values
        # print lines[-1]
        #for line in lines:
        #    stats=line.split(', ')
        #    capup.append(float(stats[2]))
        #    capdw.append(float(stats[3]))
        return capup, capdw

    # fping
    #parse fping
    def parse_fping(self, filename):
        """input: fping log at sender
        output: dataframe with all data including ignore fields"""
        clean_icmp = lambda x: int(x.strip('[').strip('],'))
        clean_avg = lambda x: float(x.strip('('))
        clean_loss = lambda x: int(x.strip('%'))
        try:
            df_fping = pd.read_csv(filename, delim_whitespace=True,
                               names=['host', 'ignore1', 'icmp_no', 'packet_size',
                                      'ignore2', 'RTT', 'ignore3', 'avg', 'ignore4',
                                      'loss', 'ignore5'],
                               converters={'icmp_no': clean_icmp,'packet_size': int,
                                           'RTT': float, 'avg': clean_avg, 'loss': clean_loss})
        except:
            subprocess.check_output("sed '$d' < "+filename+" > "+filename+"-mod", shell=True)
            df_fping = pd.read_csv(filename, delim_whitespace=True,
                               names=['host', 'ignore1', 'icmp_no', 'packet_size',
                                      'ignore2', 'RTT', 'ignore3', 'avg', 'ignore4',
                                      'loss', 'ignore5'],
                               converters={'icmp_no': clean_icmp,'packet_size': int,
                                           'RTT': float, 'avg': clean_avg, 'loss': clean_loss})

        #df[['host','RTT']].groupby('host').describe().unstack()
        return df_fping[['host', 'icmp_no', 'packet_size', 'RTT', 'avg', 'loss']]

    def get_fping_rtt(self, filename):
        """input fping log
        output describe() of fping by each host"""
        df = self.parse_fping(filename)
        df2 = df[['host', 'RTT']].groupby('host').describe().unstack()
        levels = df2.columns.levels
        labels = df2.columns.labels
        df2.columns = levels[1][labels[1]]
        return df2.T

    # ping with time
    #parse ping
    def parse_ping(self, filename):
        """input: ping log with time
        output: dataframe with all ping info"""
        df = pd.read_csv(filename, skiprows=1, sep=' ', names=['timestamp', '1','2','3','4','icmp_req','6','RTT','7'])[['timestamp','icmp_req','RTT']]
        deltatimestamp = float( df.timestamp[0].split('[')[1].split(']')[0])
        df.timestamp = df.timestamp.apply(lambda x: float( x.split('[')[1].split(']')[0] ) - deltatimestamp)
        df.icmp_req = df.icmp_req.apply(lambda z: int(z.split("=")[1]) )
        df.RTT = df.RTT.apply(lambda y: y if y is np.NaN else float(y.split("=")[1]))
        return df

    def get_ping_loss(self, filename):
        """input ping log
        output dataframe of time: lost ping"""
        pings = self.parse_ping(filename)
        if len(pings) == 0:
            return pd.DataFrame()
        icmp_seq_start = pings.icmp_req[:1]
        icmp_seq_end = pings.icmp_req[-1:]
        df2 = pd.DataFrame({'icmp_req': range(icmp_seq_start, icmp_seq_end)})
        df3 = df2.merge(pings, on='icmp_req', how='outer')
        df3.timestamp = df3.timestamp.interpolate()
        df3 = df3.fillna(-1)
        return df3[df3.RTT == -1]

    def get_ping_rtt(self, filename):
        """input ping log
        output describe() of log including number lost"""
        pings = self.parse_ping(filename)
        df = pings.RTT.describe().to_dict()
        df['loss'] = len(get_ping_loss(filename))
        return pd.Series(df)
