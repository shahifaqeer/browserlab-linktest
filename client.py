#!/usr/bin/env python

#CLIENT
from __future__ import division
from cmds import Experiment
from classes import Router

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

def experiment_suit_testbed_default(e):

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

def experiment_suit_testbed_all(e):

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
    if e.collect_calibrate:
        e.run_calibrate()                       # 120 + 20 = 140 s
    else:
        print "not doing calibrate"

    # shaperprobe
    # udp bandwidth                         # 15 * 3 + 15 * 3 = 90 s
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe AS " +str(e.experiment_counter)
    e.run_udpprobe(e.probe_udp_AS, 'AS_pro')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf AS " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_AS, 'AS_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf AS " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_AS, 'AS_tcp')
    e.blast = 1
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf bla AS " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_AS, 'AS_bla')
    e.blast = 0

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe AR " +str(e.experiment_counter)
    e.run_udpprobe(e.probe_udp_AR, 'AR_pro')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf AR " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_AR, 'AR_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf AR " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_AR, 'AR_tcp')
    e.blast=1
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf bla AR " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_AR, 'AR_bla')
    e.blast =0

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe RS " +str(e.experiment_counter)
    e.run_udpprobe(e.probe_udp_RS, 'RS_pro')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf RS " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_RS, 'RS_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf RS " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_RS, 'RS_tcp')
    e.blast=1
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf bla RS " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_RS, 'RS_bla')
    e.blast=0

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf SA " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_SA, 'SA_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf SA " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_SA, 'SA_tcp')
    e.blast=1
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf bla SA " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_SA, 'SA_bla')
    e.blast=0

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf RA " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_RA, 'RA_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf RA " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_RA, 'RA_tcp')
    e.blast=1
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf blast RA " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_RA, 'RA_bla')
    e.blast=0

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf SR " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_SR, 'SR_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf SR " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_SR, 'SR_tcp')
    e.blast=1
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf blast SR " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_SR, 'SR_bla')
    e.blast=0



    e.increment_experiment_counter()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 10 sec before next run"
    time.sleep(1)                          # 1 s wait before next suit

    return

def experiment_suit_testbed_tcp(e):

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
    if e.collect_calibrate:
        e.run_calibrate()                       # 120 + 20 = 140 s
    else:
        print "not doing calibrate"

    e.parallel = 1
    # shaperprobe
    # udp bandwidth                         # 15 * 3 + 15 * 3 = 90 s
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf AS " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_AS, 'AS_tcp')

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf AR " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_AR, 'AR_tcp')

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf RS " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_up_RS, 'RS_tcp')

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf SA " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_SA, 'SA_tcp')

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf RA " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_RA, 'RA_tcp')

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf SR " +str(e.experiment_counter)
    e.run_experiment(e.netperf_tcp_dw_SR, 'SR_tcp')

    e.increment_experiment_counter()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 10 sec before next run"
    time.sleep(1)                          # 1 s wait before next suit

    return

def experiment_suit_testbed_udp(e):

    e.blast = 1
    e.rate_blast = '1000'

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
    if e.collect_calibrate:
        e.run_calibrate()                       # 120 + 20 = 140 s
    else:
        print "not doing calibrate"

    # shaperprobe
    # udp bandwidth                         # 15 * 3 + 15 * 3 = 90 s
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf bla AS " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_AS, 'AS_bla')

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf bla AR " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_AR, 'AR_bla')

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf bla RS " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_up_RS, 'RS_bla')

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf bla SA " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_SA, 'SA_bla')

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf blast RA " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_RA, 'RA_bla')

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf blast SR " +str(e.experiment_counter)
    e.run_experiment(e.iperf_udp_dw_SR, 'SR_bla')

    e.increment_experiment_counter()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 2 sec before next run"
    time.sleep(2)                          # 1 s wait before next suit

    return

def real_udp_probes(e, OTHER_NODE=False):
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe AS " +str(e.experiment_counter)
    e.run_udpprobe(e.probe_udp_AS, 'AS_pro')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe AR " +str(e.experiment_counter)
    e.run_udpprobe(e.probe_udp_AR, 'AR_pro')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe RS " +str(e.experiment_counter)
    e.run_udpprobe(e.probe_udp_RS, 'RS_pro')

    if OTHER_NODE:
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe AB " +str(e.experiment_counter)
        e.run_udpprobe(e.probe_udp_AR, 'AR_pro')
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run probe BS " +str(e.experiment_counter)
        e.run_udpprobe(e.probe_udp_RS, 'RS_pro')

    return

def real_udp_perf(e, OTHER_NODE=False):
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp AS " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_udp_up_AS, 'AS_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp AR " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_udp_up_AR, 'AR_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp RS " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_udp_up_RS, 'RS_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp SA " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_udp_dw_SA, 'SA_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp RA " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_udp_dw_RA, 'RA_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp SR " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_udp_dw_SR, 'SR_udp')

    if OTHER_NODE:
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp AB " +str(e.experiment_counter)
        e.run_experiment(e.iperf_udp_up_AB, 'AB_udp')
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp BS " +str(e.experiment_counter)
        e.run_experiment(e.iperf_udp_up_BS, 'BS_udp')
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp BA " +str(e.experiment_counter)
        e.run_experiment(e.iperf_udp_dw_BA, 'BA_udp')
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp SB " +str(e.experiment_counter)
        e.run_experiment(e.iperf_udp_dw_SB, 'SB_udp')

    return

def real_tcp_perf(e, OTHER_NODE=False):
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf AS " +str(e.experiment_counter)
    e.run_only_experiment(e.netperf_tcp_up_AS, 'AS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf AR " +str(e.experiment_counter)
    e.run_only_experiment(e.netperf_tcp_up_AR, 'AR_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf RS " +str(e.experiment_counter)
    e.run_only_experiment(e.netperf_tcp_up_RS, 'RS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf SA " +str(e.experiment_counter)
    e.run_only_experiment(e.netperf_tcp_dw_SA, 'SA_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf RA " +str(e.experiment_counter)
    e.run_only_experiment(e.netperf_tcp_dw_RA, 'RA_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf SR " +str(e.experiment_counter)
    e.run_only_experiment(e.netperf_tcp_dw_SR, 'SR_tcp')

    if OTHER_NODE:
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf AB " +str(e.experiment_counter)
        e.run_experiment(e.netperf_tcp_up_AB, 'AB_tcp')
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf BS " +str(e.experiment_counter)
        e.run_experiment(e.netperf_tcp_up_BS, 'BS_tcp')
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf BA " +str(e.experiment_counter)
        e.run_experiment(e.netperf_tcp_dw_BA, 'BA_tcp')
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf SB " +str(e.experiment_counter)
        e.run_experiment(e.netperf_tcp_dw_SB, 'SB_tcp')
    return

def real_udp_perf2(e):
    # with reverse test
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp AS " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_udp_up_AS, 'AS_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp AR " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_udp_up_AR, 'AR_udp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run perf udp RS " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_udp_up_RS, 'RS_udp')
    return

def real_tcp_perf2(e,):
    # iperf reverse mode
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf AS " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_tcp_up_AS, 'AS_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf AR " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_tcp_up_AR, 'AR_tcp')
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run iperf RS " +str(e.experiment_counter)
    e.run_only_experiment(e.iperf_tcp_up_RS, 'RS_tcp')
    return

def experiment_suit_real_all(e):

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
    if e.collect_calibrate:
        e.run_calibrate()                       # 120 + 20 = 140 s
    else:
        print "not doing calibrate"

    # shaperprobe
    # udp bandwidth                         # 15 * 3 + 15 * 3 = 90 s

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run no traff " +str(e.experiment_counter)
    e.run_only_experiment(e.no_traffic, 'no_tra')

    #real_udp_probes(e)
    #e.get_udpprobe_rate()
    #real_udp_perf(e)
    real_tcp_perf(e)

    #e.blast=1
    #real_udp_perf(e)
    #e.blast=0

    e.increment_experiment_counter()
    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 5 sec before next run"
    time.sleep(5)                          # 1 s wait before next suit

    return


def try_job():
    measurement_folder_name = raw_input('Enter measurement name: ')
    tot_runs = int(raw_input('how many runs?'))
    e = Experiment(measurement_folder_name)
    print 'Try experiment; tot_runs: ', tot_runs
    e.run_experiment(e.iperf_tcp_dw_RA, 'RA_tcp')
    print 'DONE!'
    return


def test_measurements(tot_runs, rate, timeout, comment=''):

    rate_bit = str(rate * 8)
    timeout_sec = str(timeout)
    rate_byte = str(rate)
    Q = Router('192.168.1.1', 'root', 'passw0rd')

    if rate != 0 and rate_byte != '0':
        Q.remoteCommand('sh ratelimit3.sh eth0 '+rate_byte)
        Q.remoteCommand('sh ratelimit3.sh eth1 '+rate_byte)
        Q.remoteCommand('tc qdisc del dev br-lan root;tc qdisc add dev br-lan root netem delay 40ms;tc qdisc show dev br-lan')
    else:
        Q.remoteCommand('tc qdisc del dev eth0 root')
        Q.remoteCommand('tc qdisc del dev eth1 root')
        #Q.remoteCommand('tc qdisc del dev br-lan root')

    Q.host.close()

    if comment != '':
        e = Experiment('hnl1_access_'+rate_bit+'Mbps_timeout_'+timeout_sec+'_'+comment)
    else:
        e = Experiment('hnl1_access_'+rate_bit+'Mbps_timeout_'+timeout_sec)

    e.collect_calibrate = False
    e.set_udp_rate_mbit(rate * 8)
    e.set_test_timeout(timeout)
    e.set_test_timeout(timeout)

    for nruns in range(tot_runs):
        print "\n\t\t RUN : " + str(nruns) + " rate : " + rate_bit + "Mbps\n"
        experiment_suit_testbed_all(e)
        #experiment_suit_testbed_udp(e)
        time.sleep(1)

    Q = Router('192.168.1.1', 'root', 'passw0rd')
    Q.remoteCommand('tc qdisc del dev eth0 root')
    Q.remoteCommand('tc qdisc del dev eth1 root')
    Q.remoteCommand('tc qdisc del dev br-lan root')
    Q.host.close()

    e.transfer_all_later()

    e.kill_all()
    e.clear_all()

    return e

def real_measurements(calibrate=False, timeout=5):

    measurement_folder_name = raw_input('Enter measurement name: ')
    tot_runs = raw_input('how many runs? each run should last around 5-6 mins - I suggest at least 30 with laptop in the same location. ')

    try:
        tot_runs = int(tot_runs)
    except Exception:
        tot_runs = 1
        print "Error. Running "+str(tot_runs)+" measurement."


    e = Experiment(measurement_folder_name)
    e.collect_calibrate = calibrate

    e.use_iperf_timeout = 1
    e.timeout = timeout
    e.tcpdump = 0

    for nruns in range(tot_runs):
        print "\n\t\tRUN : " + str(nruns) + "\n"

        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
        if e.collect_calibrate:
            e.run_calibrate()                       # 120 + 20 = 140 s
        else:
            print "not doing calibrate"

        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run no traff " +str(e.experiment_counter)
        e.run_experiment(e.no_traffic, 'no_tra')

        e.get_udpprobe_rate()
        real_udp_perf(e)
        real_tcp_perf(e)
        real_udp_probes(e)
        e.blast=1
        #e.set_udp_rate_mbit(100,100,300)
        real_udp_perf(e)
        e.blast=0

        e.increment_experiment_counter()
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 5 sec before next run"
        time.sleep(5)                          # 1 s wait before next suit

    e.transfer_all_later()

    e.kill_all(1)
    e.clear_all()
    return e


def measure_iperf_sizes(folder_name, tot_runs, to, bits, calibrate=False):

    e = Experiment(folder_name)
    e.collect_calibrate = calibrate

    e.use_iperf_timeout = 0
    e.timeout = to

    e.num_bits_to_send = bits

    for nruns in range(tot_runs):
        print "\n\t\tbits: "+bits+"; RUN : " + str(nruns) + "\n"

        experiment_suit_real_all(e)
        time.sleep(1)

    e.transfer_all_later()

    e.kill_all(1)
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


def udp_test_real_measurements(calibrate=False, timeout=5):

    measurement_folder_name = raw_input('Enter measurement name: ')
    tot_runs = raw_input('how many runs? each run should last around 5-6 mins - I suggest at least 30 with laptop in the same location. ')

    try:
        tot_runs = int(tot_runs)
    except Exception:
        tot_runs = 1
        print "Error. Running "+str(tot_runs)+" measurement."

    e = Experiment(measurement_folder_name)
    e.collect_calibrate = calibrate

    e.use_iperf_timeout = 1
    e.timeout = timeout
    e.tcpdump = 1

    for nruns in range(tot_runs):
        print "\n\t\tRUN : " + str(nruns) + "\n"

        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
        if e.collect_calibrate:
            e.run_calibrate()                       # 120 + 20 = 140 s
        else:
            print "not doing calibrate"

        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run no traff " +str(e.experiment_counter)
        e.run_experiment(e.no_traffic, 'no_tra')

        #real_tcp_perf(e)
        real_udp_probes(e)
        e.get_udpprobe_rate(1)
        real_udp_perf(e)
        e.get_udpprobe_rate(0)
        real_udp_perf(e)

        e.set_udp_rate_mbit(10,10,10)
        real_udp_perf(e)
        e.set_udp_rate_mbit(20,20,20)
        real_udp_perf(e)
        e.set_udp_rate_mbit(40,40,40)
        real_udp_perf(e)
        e.set_udp_rate_mbit(60,60,60)
        real_udp_perf(e)
        e.set_udp_rate_mbit(80,80,80)
        real_udp_perf(e)
        e.set_udp_rate_mbit(100,100,100)
        real_udp_perf(e)
        e.set_udp_rate_mbit(150,150,150)
        real_udp_perf(e)

        e.increment_experiment_counter()
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 5 sec before next run"
        time.sleep(5)                          # 1 s wait before next suit

    e.transfer_all_later()

    e.kill_all(1)
    e.clear_all()
    return e

def measure_iperf_tcp_duration_streams(folder_name, tot_runs, timeout, num_par=10, calibrate=False):

    e = Experiment(folder_name)
    e.collect_calibrate = calibrate

    e.use_iperf_timeout = 1
    e.timeout = timeout
    e.num_parallel_streams = num_par

    for nruns in range(tot_runs):
        print "\n\t\tduration: "+str(timeout)+"; parallel: "+str(num_par)+"; RUN: " + str(nruns) + "\n"
        experiment_suit_real_all(e)
        #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf AR " +str(e.experiment_counter)
        #e.run_only_experiment(e.netperf_tcp_up_AR, 'AR_tcp')
        #print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run netperf RA " +str(e.experiment_counter)
        #e.run_only_experiment(e.netperf_tcp_dw_RA, 'RA_tcp')
        time.sleep(1)

    e.transfer_all_later()

    e.kill_all(1)
    e.clear_all()
    return e

def measure_iperf_udp_bandwidth_ratios(measurement_folder_name, tot_runs, timeout, calibrate=False):
    e = Experiment(measurement_folder_name)
    e.collect_calibrate = calibrate

    e.use_iperf_timeout = 1
    e.timeout = timeout
    e.tcpdump = 1
    e.parallel = 0
    e.udp = 1

    for nruns in range(tot_runs):
        print "\n\t\tUDP duration: "+str(timeout)+"; RUN : " + str(nruns) + "\n"

        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
        if e.collect_calibrate:
            e.run_calibrate()                       # 120 + 20 = 140 s
        else:
            print "not doing calibrate"

        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run no traff " +str(e.experiment_counter)
        e.run_experiment(e.no_traffic, 'no_tra')

        e.set_udp_rate_mbit(10,10,10)
        #real_udp_perf(e)
        real_udp_perf2(e)
        e.set_udp_rate_mbit(100,100,100)
        #real_udp_perf(e)
        real_udp_perf2(e)

        #SHAPERPROBE
        #real_udp_probes(e)
        #e.get_udpprobe_rate(1)
        #real_udp_perf(e)
        #e.get_udpprobe_rate(0)
        #real_udp_perf(e)

        e.increment_experiment_counter()
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Wait 5 sec before next run"
        time.sleep(5)                          # 1 s wait before next suit

    e.transfer_all_later()

    e.kill_all(1)
    e.clear_all()

    return

def parallel_duration_run_suit():
    # TCP
    print "START ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    starttime = time.time()

    measurement_folder_name = raw_input('Enter measurement name: ')
    tot_runs = raw_input('how many runs? each run should last around 5-6 mins - I suggest at least 30 with laptop in the same location. ')

    try:
        tot_runs = int(tot_runs)
    except Exception:
        tot_runs = 1
        print "Error. Running "+str(tot_runs)+" measurement."

    e = Experiment()
    e.collect_calibrate = False
    e.use_iperf_timeout = 1

    all_folder_name_list = []

    for nruns in range(tot_runs):
        #for num_par in [1, 2, 3, 4, 5, 10]:
        #    for timeout in [2, 5, 10, 15]:
        for num_par in [1, 10]:
            for timeout in [10]:
                print "\n\t\tTCP duration: "+str(timeout)+"; parallel: "+str(num_par)+"; RUN: " + str(nruns) + "\n"

                folder_name = measurement_folder_name + '_tcp_duration_' + str(timeout) + '_parallel_' + str(num_par)

                if not folder_name in all_folder_name_list:
                    all_folder_name_list.append(folder_name)

                e.timeout = timeout
                e.num_parallel_streams = num_par
                e.set_unique_id(folder_name)

                print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run no traff " +str(e.experiment_counter)
                e.run_only_experiment(e.no_traffic, 'no_tra')

                #real_tcp_perf(e)
                real_tcp_perf2(e)

    for folder_name in all_folder_name_list:
        e.set_unique_id(folder_name)
        e.transfer_all_later()
        e.kill_all(1)
        e.clear_all()

    # FOLLOW UP WITH UDP
    timeout=2
    folder_name = measurement_folder_name + '_udp_duration_'+str(timeout)
    measure_iperf_udp_bandwidth_ratios(folder_name, tot_runs, timeout, False)

    print "DONE ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    endtime = time.time()

    print "\n Total time taken = ", endtime - starttime

    return

def compare_all_techniques(NUM_PARALLEL=[1,3,5,10], TIMEOUTS=[2,5,10]):

    measurement_folder_name = raw_input('Enter measurement name: ')
    tot_runs = raw_input('how many runs? each run should last around 5-6 mins - I suggest at least 30 with laptop in the same location. ')

    try:
        tot_runs = int(tot_runs)
    except Exception:
        tot_runs = 1
        print "Error. Running "+str(tot_runs)+" measurement."

    e = Experiment()
    # set all to yes
    e.collect_calibrate = False
    e.use_iperf_timeout = 1
    e.USE_IPERF3 = 1
    e.USE_IPERF_REV = 1
    e.USE_UDP_PROBE = 1
    e.USE_NETPERF = 0
    e.tcp = 1
    e.udp = 1
    e.start_servers()
    e.WTF_enable = 0

    all_folder_name_list = []

    for nruns in range(tot_runs):
        for timeout in TIMEOUTS:

            for num_par in NUM_PARALLEL:
                print "\n\t\tTCP duration: "+str(timeout)+"; parallel: "+str(num_par)+"; RUN: " + str(nruns) + "\n"

                folder_name = measurement_folder_name + '_tcp_duration_' + str(timeout) + '_parallel_' + str(num_par)
                if not folder_name in all_folder_name_list:
                    all_folder_name_list.append(folder_name)

                e.timeout = timeout
                if num_par > 1:
                    e.parallel = 1
                else:
                    e.parallel = 0
                e.num_parallel_streams = num_par
                e.set_unique_id(folder_name)

                e.run_only_experiment(e.no_traffic, 'no_tra')
                #iperf_tcp(e)
                iperf3_tcp(e)
                #netperf_tcp(e)
            #UDP
            folder_name = measurement_folder_name + '_udp_duration_'+str(timeout)
            if not folder_name in all_folder_name_list:
                all_folder_name_list.append(folder_name)
            e.set_unique_id(folder_name)
            e.set_udp_rate_mbit(128,100,150)
            e.parallel = 0
            #iperf3
            #iperf3_udp(e)
            #iperf
            iperf_udp(e)
            #udp probe
            probe_udp(e)

    return e, all_folder_name_list

# iperf
def iperf_tcp(e):
    e.run_only_experiment(e.iperf_tcp_up_AS, 'AS_tcp')
    e.run_only_experiment(e.iperf_tcp_up_AR, 'AR_tcp')
    e.run_only_experiment(e.iperf_tcp_up_RS, 'RS_tcp')
    e.run_only_experiment(e.iperf_tcp_dw_SA, 'SA_tcp')
    e.WTF_enable = 1
    e.run_only_experiment(e.iperf_tcp_dw_SA, 'SA_tcp')
    e.WTF_enable = 0
    e.run_only_experiment(e.iperf_tcp_dw_RA, 'RA_tcp')
    e.run_only_experiment(e.iperf_tcp_dw_SR, 'SR_tcp')
    return

#iperf3
def iperf3_tcp(e):
    e.WTF_enable = 1
    e.run_only_experiment(e.iperf3_tcp_up_AS, 'AS_tcp')
    e.WTF_enable = 0
    e.run_only_experiment(e.iperf3_tcp_up_AR, 'AR_tcp')
    e.run_only_experiment(e.iperf3_tcp_up_RS, 'RS_tcp')
    e.WTF_enable = 1
    e.run_only_experiment(e.iperf3_tcp_dw_SA, 'SA_tcp')
    e.WTF_enable = 0
    e.run_only_experiment(e.iperf3_tcp_dw_RA, 'RA_tcp')
    e.run_only_experiment(e.iperf3_tcp_dw_SR, 'SR_tcp')
    return

#netperf
def netperf_tcp(e):
    e.run_only_experiment(e.netperf_tcp_up_AS, 'AS_tcp')
    e.run_only_experiment(e.netperf_tcp_up_AR, 'AR_tcp')
    e.run_only_experiment(e.netperf_tcp_up_RS, 'RS_tcp')
    e.run_only_experiment(e.netperf_tcp_dw_SA, 'SA_tcp')
    e.run_only_experiment(e.netperf_tcp_dw_RA, 'RA_tcp')
    e.run_only_experiment(e.netperf_tcp_dw_SR, 'SR_tcp')
    return

def iperf3_udp(e):
    e.run_only_experiment(e.iperf3_udp_up_AS, 'AS_udp')
    e.run_only_experiment(e.iperf3_udp_up_AR, 'AR_udp')
    e.run_only_experiment(e.iperf3_udp_up_RS, 'RS_udp')
    e.run_only_experiment(e.iperf3_udp_dw_SA, 'SA_udp')
    e.run_only_experiment(e.iperf3_udp_dw_RA, 'RA_udp')
    e.run_only_experiment(e.iperf3_udp_dw_SR, 'SR_udp')
    return

def iperf_udp(e):
    e.WTF_enable = 1
    e.run_only_experiment(e.iperf_udp_up_AS, 'AS_udp')
    e.WTF_enable = 0
    e.run_only_experiment(e.iperf_udp_up_AR, 'AR_udp')
    e.run_only_experiment(e.iperf_udp_up_RS, 'RS_udp')
    e.WTF_enable = 1
    e.run_only_experiment(e.iperf_udp_dw_SA, 'SA_udp')
    e.WTF_enable = 0
    e.run_only_experiment(e.iperf_udp_dw_RA, 'RA_udp')
    e.run_only_experiment(e.iperf_udp_dw_SR, 'SR_udp')
    return

def probe_udp(e):
    e.run_only_experiment(e.probe_udp_AR, 'AR_udp')
    e.run_only_experiment(e.probe_udp_AS, 'AS_udp')
    e.run_only_experiment(e.probe_udp_RS, 'RS_udp')
    return

def transfer_all_folder_names(e, all_folder_name_list):

    for folder_name in all_folder_name_list:
        e.set_unique_id(folder_name)
        e.transfer_all_later()
        e.kill_all(1)
        e.clear_all()

    print "DONE Transfer ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    return

def main_testbed_compare(rate=4):

    rate_bit = str(rate * 8)
    rate_byte = str(rate)

    Q = Router('192.168.1.1', 'root', 'passw0rd')
    Q.remoteCommand('tc qdisc del dev br-lan root;tc qdisc add dev br-lan root netem delay 40ms;tc qdisc show dev br-lan')

    if rate != 0 and rate_byte != '0':
        Q.remoteCommand('sh ratelimit3.sh eth0 '+rate_byte)
        Q.remoteCommand('sh ratelimit3.sh eth1 '+rate_byte)
    else:
        Q.remoteCommand('tc qdisc del dev eth0 root')
        Q.remoteCommand('tc qdisc del dev eth1 root')
        #Q.remoteCommand('tc qdisc del dev br-lan root')
    Q.host.close()


    print "START ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    starttime = time.time()

    e, all_folder_name_list = compare_all_techniques([1,2,3,4,5,6,7,8,9,10],[5])
    #e, all_folder_name_list = compare_all_techniques()

    print "DONE ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    endtime = time.time()

    print "\n Total time taken = ", endtime - starttime

    Q = Router('192.168.1.1', 'root', 'passw0rd')
    Q.remoteCommand('tc qdisc del dev br-lan root;tc qdisc del dev eth0 root;tc qdisc del dev eth1 root')
    subprocess.check_output('sudo ifconfig eth0 up', shell=True)

    transfer = 'y'
    #transfer = raw_input("start transfer... [y]")

    if transfer == 'y' or transfer == 'Y':
        transfer_all_folder_names(e, all_folder_name_list)

    endtime2 = time.time()
    print "\n Total transfer time = ", endtime2 - endtime

    subprocess.check_output('sudo ifconfig eth0 down', shell=True)
    return e

def ping_buffer_endhost_test():

    print "START ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    starttime = time.time()

    measurement_folder_name = raw_input('Enter measurement name: ')
    tot_runs = raw_input('how many runs? each run should last around 5-6 mins - I suggest at least 30 with laptop in the same location. ')

    try:
        tot_runs = int(tot_runs)
    except Exception:
        tot_runs = 1
        print "Error. Running "+str(tot_runs)+" measurement."

    e = Experiment(measurement_folder_name)
    # set all to yes
    e.collect_calibrate = False
    e.use_iperf_timeout = 1
    e.USE_IPERF3 = 1
    e.USE_IPERF_REV = 1
    e.USE_UDP_PROBE = 0
    e.USE_NETPERF = 0
    e.tcp = 1
    e.udp = 1
    e.start_servers()
    e.WTF_enable = 1
    e.timeout = 5
    e.parallel = 1
    e.num_parallel_streams = 4


    for nruns in range(tot_runs):
        e.run_only_experiment(e.no_traffic, 'no_tra')
        e.run_only_experiment(e.iperf3_tcp_up_AS, 'AS_tcp')
        e.run_only_experiment(e.iperf3_tcp_dw_SA, 'SA_tcp')
        #e.run_only_experiment(e.iperf_tcp_up_AS, 'AS_tcp')
        #e.run_only_experiment(e.iperf_tcp_dw_SA, 'SA_tcp')

        e.parallel = 0
        e.run_only_experiment(e.iperf_udp_up_AS, 'AS_udp')
        e.run_only_experiment(e.iperf_udp_dw_SA, 'SA_udp')

        time.sleep(5)

    print "DONE ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    endtime = time.time()
    print "\n Total time taken = ", endtime - starttime

    e.transfer_all_later()

    e.kill_all(1)
    e.clear_all()

    endtime2 = time.time()
    print "\n Total transfer time = ", endtime2 - endtime

    return e

def bottleneck_vs_scenario():

    measurement_folder_name = raw_input('Enter measurement name: ')
    tot_runs = raw_input('how many runs? each run should last around 5-6 mins - I suggest at least 30 with laptop in the same location. ')

    try:
        tot_runs = int(tot_runs)
    except Exception:
        tot_runs = 1
        print "Error. Running "+str(tot_runs)+" measurement."

    e = Experiment()
    # set all to yes
    e.collect_calibrate = False
    e.use_iperf_timeout = 1
    e.USE_IPERF3 = 1
    e.USE_IPERF_REV = 1
    e.USE_UDP_PROBE = 1
    e.USE_NETPERF = 0
    e.tcp = 1
    e.udp = 1
    e.start_servers()
    e.WTF_enable = 1
    e.timeout = 5
    e.num_parallel_streams = 4

    print "START ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    starttime = time.time()

    all_folder_name_list = []

    for rate in range(16):

        rate_bit = str(rate * 8)
        rate_byte = str(rate)

        folder_name = measurement_folder_name + '_access_' + str(rate_bit)
        if not folder_name in all_folder_name_list:
            all_folder_name_list.append(folder_name)
        e.set_unique_id(folder_name)

        Q = Router('192.168.1.1', 'root', 'passw0rd')
        Q.remoteCommand('tc qdisc del dev br-lan root;tc qdisc add dev br-lan root netem delay 40ms;tc qdisc show dev br-lan')
        if rate != 0 and rate_byte != '0':
            Q.remoteCommand('sh ratelimit3.sh eth0 '+rate_byte)
            Q.remoteCommand('sh ratelimit3.sh eth1 '+rate_byte)
        else:
            Q.remoteCommand('tc qdisc del dev eth0 root')
            Q.remoteCommand('tc qdisc del dev eth1 root')
            #Q.remoteCommand('tc qdisc del dev br-lan root')
        Q.host.close()

        for runs in range(tot_runs):
            e.parallel = 1
            e.run_only_experiment(e.no_traffic, 'no_tra')
            #iperf3_tcp
            e.run_only_experiment(e.iperf3_tcp_up_AS, 'AS_tcp')
            e.run_only_experiment(e.iperf3_tcp_up_AR, 'AR_tcp')
            e.run_only_experiment(e.iperf3_tcp_up_RS, 'RS_tcp')
            e.run_only_experiment(e.iperf3_tcp_dw_SA, 'SA_tcp')
            e.run_only_experiment(e.iperf3_tcp_dw_RA, 'RA_tcp')
            e.run_only_experiment(e.iperf3_tcp_dw_SR, 'SR_tcp')
            #iperf_udp
            e.parallel = 0
            e.run_only_experiment(e.iperf_udp_up_AS, 'AS_udp')
            e.run_only_experiment(e.iperf_udp_dw_SA, 'SA_udp')
            #probe_udp
            e.run_only_experiment(e.probe_udp_AR, 'AR_udp')
            e.run_only_experiment(e.probe_udp_AS, 'AS_udp')
            e.run_only_experiment(e.probe_udp_RS, 'RS_udp')

    print "DONE ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    endtime = time.time()

    print "\n Total time taken = ", endtime - starttime

    # Transfer to server
    Q = Router('192.168.1.1', 'root', 'passw0rd')
    Q.remoteCommand('tc qdisc del dev br-lan root;tc qdisc del dev eth0 root;tc qdisc del dev eth1 root')
    subprocess.check_output('sudo ifconfig eth0 up', shell=True)
    time.sleep(5)
    transfer = 'y'
    #transfer = raw_input("start transfer... [y]")
    if transfer == 'y' or transfer == 'Y':
        transfer_all_folder_names(e, all_folder_name_list)
    subprocess.check_output('sudo ifconfig eth0 down', shell=True)

    endtime2 = time.time()
    print "\n Total transfer time = ", endtime2 - endtime
    print "\n Total script time = ", endtime2 - starttime

    return e


if __name__ == "__main__":

    #ping_buffer_endhost_test()

    e = bottleneck_vs_scenario()

    e = main_testbed_compare(15)

    #parallel_duration_run_suit()
    # TCP
    #measurement_folder_name = raw_input('Enter measurement name: ')
    #tot_runs = raw_input('how many runs? each run should last around 5-6 mins - I suggest at least 30 with laptop in the same location. ')

    #try:
    #    tot_runs = int(tot_runs)
    #except Exception:
    #    tot_runs = 1
    #    print "Error. Running "+str(tot_runs)+" measurement."

    #for num_par in [1, 2, 3, 4, 5, 10]:
    #    for timeout in [2, 5, 10, 15]:
    #       folder_name = measurement_folder_name + '_tcp_duration_' + str(timeout) + '_parallel_' + str(num_par)
    #       measure_iperf_tcp_duration_streams(folder_name, tot_runs, timeout, num_par, False)

    #timeout=2
    #folder_name = measurement_folder_name + '_udp_duration_'+str(timeout)
    #measure_iperf_udp_bandwidth_ratios(folder_name, tot_runs, timeout, False)
    # UDP


    #timeout = iter([0.1, 0.11, 0.15, 0.9, 8.1, 15.5])

    #for bits in ['10K', '100K', '1M', '10M', '100M', '1000M']:
    #    folder_name = measurement_folder_name + '_' + bits
    #    to = timeout.next()


        #measure_iperf_sizes(folder_name, tot_runs, to, bits, False)

        #comment = raw_input('Enter measurement comment: ')
    #tot_runs = raw_input('how many runs? each run should last around 5-6 mins - I suggest at least 30 with laptop in the same location. ')

    #try:
    #    tot_runs = int(tot_runs)
    #except Exception:
    #    tot_runs = 1
    #    print "Error. Running "+str(tot_runs)+" measurement."


    #for rate in [1, 3, 5 ,7, 9, 11, 13, 15]:
    #    for timeout in [2, 5, 10]:
    #        test_measurements(tot_runs, rate, timeout, comment)
