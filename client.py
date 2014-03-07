#!/usr/bin/env python

#CLIENT
from __future__ import division
from commands import Experiment, Router

import time
#import schedule

#time_wait = 20 # wait 20 sec before each experiment


def experiment_suit(e):

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
    # Total ~ 430 s ~ 7:10 mins
    if e.collect_calibrate:
        # e.run_calibrate()                       # 120 + 20 = 140 s
    else:
        print "not doing calibrate"
    #time.sleep(time_wait)
    # latency without load
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run No Traffic"
    # Total ~ 430 s ~ 7:10 mins
    e.run_experiment(e.no_traffic)          # 12 + 15 = 27 s
    #time.sleep(time_wait)
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf AS"
    # tcp bw and latency under load         # 12 * 6 + 15 * 6 = 172 s
    e.run_experiment(e.iperf_tcp_up_AS)
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf SA"
    #time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_dw_SA)
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf AR"
    #time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_up_AR)
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf RA"
    #time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_dw_RA)
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf RS"
    #time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_up_RS)
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf SR"
    #time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_dw_SR)
    #time.sleep(time_wait)
    # udp bandwidth                         # 15 * 3 + 15 * 3 = 90 s
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe AR"
    e.run_experiment(e.probe_udp_AR)
    #time.sleep(time_wait)
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe AS"
    e.run_experiment(e.probe_udp_AS)
    #time.sleep(time_wait)
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe RS"
    e.run_experiment(e.probe_udp_RS)
    #time.sleep(time_wait)
    e.increment_experiment_counter()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 60 sec before next run"
    time.sleep(60)                          # 60 s wait before next suit

    return


def try_job():
    measurement_folder_name = raw_input('Enter measurement name: ')
    tot_runs = int(raw_input('how many runs?'))
    e = Experiment(measurement_folder_name)
    print 'Try experiment '
    e.run_experiment(e.iperf_tcp_dw_RA)
    print 'DONE!'
    return


def test_measurements(tot_runs, rate):

    rate = str(rate)
    Q = Router('192.168.1.1', 'root', 'passw0rd')

    if rate != 0:
        Q.remoteCommand('sh ratelimit3.sh eth0 '+rate)
        Q.remoteCommand('sh ratelimit3.sh eth1 '+rate)
    else:
        Q.remoteCommand('tc qdisc del dev eth0 root')
        Q.remoteCommand('tc qdisc del dev eth1 root')

    Q.host.close()

    e = Experiment('hnl1_'+rate+'MBps')

    for nruns in range(tot_runs):
        print "\t\t\n RUN : " + str(nruns) + "\n"
        experiment_suit(e)
        time.sleep(1)

    e.kill_all()
    e.clear_all()

    return

def real_measurements():

    measurement_folder_name = raw_input('Enter measurement name: ')
    tot_runs = int(raw_input('how many runs? each run should last around 5-6 mins - I suggest at least 50 with laptop in the same location. '))

    e = Experiment(measurement_folder_name)
    e.collect_calibrate = True

    for nruns in range(tot_runs):
        print "\t\t\n RUN : " + str(nruns) + "\n"
        experiment_suit(e)
        time.sleep(1)

    e.kill_all()
    e.clear_all()
    return


if __name__ == "__main__":


    #for rate in [1,2,3,4,6,8,12,16,20,0]:
        #tot_runs = 50
        #measure_link(tot_runs, rate)


    measure_link(30, 0)
    measure_link(30, 1)
    measure_link(30, 12)
