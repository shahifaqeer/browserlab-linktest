#!/usr/bin/env python

#CLIENT
from __future__ import division
from cmds import Experiment, Router

import time
import subprocess
#import schedule

#time_wait = 20 # wait 20 sec before each experiment


def experiment_suit(e):

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
    # Total ~ 430 s ~ 7:10 mins
    if e.collect_calibrate:
        e.run_calibrate()                       # 120 + 20 = 140 s
    else:
        print "not doing calibrate"
    # latency without load
    # Total ~ 430 s ~ 7:10 mins
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run No Traffic "+str(e.experiment_counter)
    #e.run_experiment(e.no_traffic, 'no_tra')          # 12 + 15 = 27 s
    # tcp bw and latency under load         # 12 * 6 + 15 * 6 = 172 s
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf AS " +str(e.experiment_counter)
    #e.run_experiment(e.iperf_tcp_up_AS, 'AS_tcp')
    e.run_experiment(e.netperf_tcp_up_AS, 'AS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf SA " +str(e.experiment_counter)
    #e.run_experiment(e.iperf_tcp_dw_SA, 'SA_tcp')
    e.run_experiment(e.netperf_tcp_dw_SA, 'SA_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf AR " +str(e.experiment_counter)
    #e.run_experiment(e.iperf_tcp_up_AR, 'AR_tcp')
    e.run_experiment(e.netperf_tcp_up_AR, 'AR_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf RA " +str(e.experiment_counter)
    #e.run_experiment(e.iperf_tcp_dw_RA, 'RA_tcp')
    e.run_experiment(e.netperf_tcp_dw_RA, 'RA_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf RS " +str(e.experiment_counter)
    #e.run_experiment(e.iperf_tcp_up_RS, 'RS_tcp')
    e.run_experiment(e.netperf_tcp_up_RS, 'RS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf SR " +str(e.experiment_counter)
    #e.run_experiment(e.iperf_tcp_dw_SR, 'SR_tcp')
    e.run_experiment(e.netperf_tcp_dw_SR, 'SR_tcp')
    #time.sleep(time_wait)
    # udp bandwidth                         # 15 * 3 + 15 * 3 = 90 s
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe AR"
    #e.run_experiment(e.probe_udp_AR, 'AR_udp')
    #time.sleep(time_wait)
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe AS"
    #e.run_experiment(e.probe_udp_AS, 'AS_udp')
    #time.sleep(time_wait)
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe RS"
    #e.run_experiment(e.probe_udp_RS, 'RS_udp')
    #time.sleep(time_wait)
    e.increment_experiment_counter()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 10 sec before next run"
    time.sleep(e.timeout)                          # 10 s wait before next suit

    return

def experiment_suit_no_router(e):

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf no tra " +str(e.experiment_counter)
    e.run_experiment(e.no_traffic, 'no_tra')          # 12 + 15 = 27 s
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf AS " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_AS, 'AS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf SA " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_SA, 'SA_tcp')
    e.increment_experiment_counter()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 10 sec before next run"
    time.sleep(10)                          # 10 s wait before next suit
    return

def experiment_suit_non_coop(e):

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
    # Total ~ 430 s ~ 7:10 mins
    if e.collect_calibrate:
        e.run_calibrate()                       # 120 + 20 = 140 s
    else:
        print "not doing calibrate"
    # latency without load
    # Total ~ 430 s ~ 7:10 mins
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf AS " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_AS, 'AS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf SA " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_SA, 'SA_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf BS " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_RS, 'BS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf SB " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_SR, 'SB_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf AB " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_AR, 'AB_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf BA " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_RA, 'BA_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run fabprobe SR " +str(e.experiment_counter)
    e.run_experiment(e.fabprobe_SR, 'SR_fab')
    e.increment_experiment_counter()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 10 sec before next run"
    time.sleep(10)                          # 10 s wait before next suit

    return

def experiment_suit_testbed(e):

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
    if e.collect_calibrate:
        e.run_calibrate()                       # 120 + 20 = 140 s
    else:
        print "not doing calibrate"

    # tcp bandwidth
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf AS " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_AS, 'AS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf AR " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_AR, 'AR_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf RS " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_RS, 'RS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf SA " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_SA, 'SA_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf RA " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_RA, 'RA_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf SR " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_SR, 'SR_tcp')

    # udp bandwidth                         # 15 * 3 + 15 * 3 = 90 s
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp SA"
    #e.run_experiment(e.netperf_udp_SA, 'SA_udp')

    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp RA"
    #e.run_experiment(e.netperf_udp_dw_RA, 'RA_udp')
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp AR"
    #e.run_experiment(e.netperf_udp_up_AR, 'AR_udp')

    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp SR"
    #e.run_experiment(e.netperf_udp_SR, 'SR_udp')

    e.increment_experiment_counter()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 10 sec before next run"
    time.sleep(10)                          # 10 s wait before next suit

    return

def experiment_suit_testbed_udp(e):

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
    if e.collect_calibrate:
        e.run_calibrate()                       # 120 + 20 = 140 s
    else:
        print "not doing calibrate"

    # tcp bandwidth
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf AS " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_AS, 'AS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf AR " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_AR, 'AR_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf RS " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_RS, 'RS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf SA " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_SA, 'SA_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf RA " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_RA, 'RA_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf SR " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_SR, 'SR_tcp')

    # udp bandwidth                         # 15 * 3 + 15 * 3 = 90 s
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp SA"
    #e.run_experiment(e.netperf_udp_SA, 'SA_udp')

    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp RA"
    #e.run_experiment(e.netperf_udp_dw_RA, 'RA_udp')
    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp AR"
    #e.run_experiment(e.netperf_udp_up_AR, 'AR_udp')

    #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp SR"
    #e.run_experiment(e.netperf_udp_SR, 'SR_udp')

    e.increment_experiment_counter()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 10 sec before next run"
    time.sleep(1)                          # 1 s wait before next suit

    return


def try_job():
    measurement_folder_name = raw_input('Enter measurement name: ')
    tot_runs = int(raw_input('how many runs?'))
    e = Experiment(measurement_folder_name)
    print 'Try experiment '
    e.run_experiment(e.iperf_tcp_dw_RA, 'RA_tcp')
    print 'DONE!'
    return


def test_measurements(tot_runs, rate):

    rate_bit = str(rate * 8)
    rate = str(rate)
    Q = Router('192.168.1.1', 'root', 'passw0rd')

    if rate != 0 and rate != '0':
        Q.remoteCommand('sh ratelimit3.sh eth0 '+rate)
        Q.remoteCommand('sh ratelimit3.sh eth1 '+rate)
    else:
        Q.remoteCommand('tc qdisc del dev eth0 root')
        Q.remoteCommand('tc qdisc del dev eth1 root')

    Q.host.close()

    e = Experiment('hnl1_access_'+rate_bit+'Mbps')
    e.collect_calibrate = False
    e.timeout = 5

    for nruns in range(tot_runs):
        print "\n\t\t RUN : " + str(nruns) + " rate : " + rate_bit + "Mbps\n"
        experiment_suit_testbed_udp(e)
        time.sleep(1)
        experiment_suit_testbed(e)

    Q = Router('192.168.1.1', 'root', 'passw0rd')
    Q.remoteCommand('tc qdisc del dev eth0 root')
    Q.remoteCommand('tc qdisc del dev eth1 root')
    Q.host.close()

    e.transfer_all_later()

    e.kill_all()
    e.clear_all()

    return

def real_measurements(calibrate=True):

    measurement_folder_name = raw_input('Enter measurement name: ')
    tot_runs = raw_input('how many runs? each run should last around 5-6 mins - I suggest at least 50 with laptop in the same location. ')

    try:
        tot_runs = int(tot_runs)
    except Exception:
        tot_runs = 1
        print "Error. Running "+str(tot_runs)+" measurement."

    e = Experiment(measurement_folder_name)
    e.collect_calibrate = calibrate

    for nruns in range(tot_runs):
        print "\t\t\n RUN : " + str(nruns) + "\n"
        #experiment_suit_non_coop(e)
        experiment_suit(e)
        #experiment_suit_no_router(e)
        time.sleep(1)

    #trans = raw_input("transfer now?[Y] ")
    #if trans == 'Y' or trans == 'y':
    e.transfer_all_later()

    e.kill_all()
    e.clear_all()
    return e

def remove_tc_shaping(client_int='eth0', router_int='eth0'):
    Q = Router('192.168.10.1', 'root', 'passw0rd')
    try:
        subprocess.check_output('tc qdisc del dev ' +client_int+ ' root', shell=True)
    except Exception:
        print subprocess.check_output('tc qdisc show dev ' +client_int, shell=True)
    try:
        Q.remoteCommand('tc qdisc del dev ' +router_int+ ' root')
    except Exception:
        Q.remoteCommand('tc qdisc show dev ' +router_int)
    return Q


def wired_simulation_testbed(rates, delays, tot_runs):

    client_int = 'eth0'
    router_int = 'eth0'

    for rate in rates:
        for delay in delays:
            Q = Router('192.168.1.1', 'root', 'passw0rd')
            if rate != 0:
                Q.remoteCommand('sh ratelimit3.sh eth0 '+str(rate))
                Q.remoteCommand('sh ratelimit3.sh eth1 '+str(rate))
            else:
                Q.remoteCommand('tc qdisc del dev eth0 root')
                Q.remoteCommand('tc qdisc del dev eth1 root')
            Q.host.close()

            R = remove_tc_shaping(client_int, router_int)
            if delay != 0:
                subprocess.check_output('tc qdisc add dev '+client_int+' root netem delay ' +str(delay)+ 'ms', shell=True)
                R.remoteCommand('tc qdisc add dev '+router_int+' root netem delay ' +str(delay)+ 'ms')
            R.host.close()

            measurement_folder_name = 'wired_delay_'+str(int(2*delay))+'_access_'+str(rate)
            print "\n\t\t START " + measurement_folder_name + "\n"
            time.sleep(5)

            e = Experiment(measurement_folder_name)
            e.collect_calibrate = False

            for nruns in range(tot_runs):
                print "\n\t\t RUN : " + str(nruns) + " DELAY : " + str(delay) + " ACCESS LINK RATE : " + str(rate) + "\n"
                experiment_suit(e)
                time.sleep(1)

            # transfer all with no delay and no shaping
            R = remove_tc_shaping(client_int, router_int)
            R.host.close()
            Q = Router('192.168.1.1', 'root', 'passw0rd')
            Q.remoteCommand('tc qdisc del dev eth0 root')
            Q.remoteCommand('tc qdisc del dev eth1 root')
            Q.host.close()

            e.kill_all()
            e.clear_all()
            e.transfer_all_later()

            print "\n\t\t DONE " + measurement_folder_name + "\n"

    return e


if __name__ == "__main__":

    rates = [2, 5, 10, 15, 20] #MBps
    delays = [1, 2.5, 5, 7.5, 10] #ms
    tot_runs = raw_input('how many runs? each run should last around 5-6 mins - I suggest at least 50 with laptop in the same location. ')
    try:
        tot_runs = int(tot_runs)
    except Exception:
        tot_runs = 1
        print "Error. Running "+str(tot_runs)+" measurement."

    #wired_simulation_testbed(rates, delays, tot_runs)

    #real_measurements(False)

    #tot_runs = int(raw_input("how many runs for each tc setting? "))

    for rate in [2,4,6,8,10,12,20]:
        test_measurements(tot_runs, rate)

    #measure_link(30, 0)
    #measure_link(30, 1)
    #measure_link(30, 12)
    #test_measurements(30, 0)
    #test_measurements(30, 1)
    #test_measurements(30, 12)
