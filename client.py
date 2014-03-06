#CLIENT
from __future__ import division
from commands import Experiment

import time
import schedule

#time_wait = 20 # wait 20 sec before each experiment


def experiment_suit(e):

    print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())) + ": Run Experiment Suit"
    # Total ~ 430 s ~ 7:10 mins
    e.run_calibrate()                       # 120 + 20 = 140 s
    #time.sleep(time_wait)
    # latency without load
    e.run_experiment(e.no_traffic)          # 12 + 15 = 27 s
    #time.sleep(time_wait)
    # tcp bw and latency under load         # 12 * 6 + 15 * 6 = 172 s
    e.run_experiment(e.iperf_tcp_up_AS)
    #time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_dw_SA)
    #time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_up_AR)
    #time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_dw_RA)
    #time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_up_RS)
    #time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_dw_SR)
    #time.sleep(time_wait)
    # udp bandwidth                         # 15 * 3 + 15 * 3 = 90 s
    e.run_experiment(e.probe_udp_AR)
    #time.sleep(time_wait)
    e.run_experiment(e.probe_udp_AS)
    #time.sleep(time_wait)
    e.run_experiment(e.probe_udp_RS)
    #time.sleep(time_wait)
    e.increment_experiment_counter()
    print "WAIT 60 s before next run"
    time.sleep(60)                          # 60 s wait before next suit

    return


def try_job():
    e = Experiment()
    print 'Try experiment '
    e.run_experiment(e.iperf_tcp_dw_RA)
    print 'DONE!'
    return


if __name__ == "__main__":

    measurement_folder_name = raw_input('Enter measurement name: ')

    e = Experiment(measurement_folder_name)

    schedule.every(10).minutes.do(experiment_suit, e)
    #schedule.every(1).minutes.do(try_job)

    experiment_suit(e)

    while True:
        schedule.run_pending()
        time.sleep(1)
