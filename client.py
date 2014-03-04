#CLIENT
from __future__ import division
from commands import Experiment

import time
import schedule

time_wait = 20 # wait 20 sec before each experiment


def experiment_suit():
    e = Experiment()                        # Total ~ 470 s ~ 7:50 mins

    print "RUN Experiment"
    e.run_passive()                         # 120 + 20 = 140 s
    time.sleep(time_wait)
    # latency without load
    e.run_experiment(e.no_traffic)          # 12 + 20 = 32 s
    time.sleep(time_wait)
    # tcp bw and latency under load         # 12 * 6 + 20 * 6 = 192 s
    e.run_experiment(e.iperf_tcp_up_AS)
    time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_dw_SA)
    time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_up_AR)
    time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_dw_RA)
    time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_up_RS)
    time.sleep(time_wait)
    e.run_experiment(e.iperf_tcp_dw_SR)
    time.sleep(time_wait)
    # udp bandwidth                         # 12 * 3 + 20 * 3 = 96 s
    e.run_experiment(e.probe_udp_AR)
    time.sleep(time_wait)
    e.run_experiment(e.probe_udp_AS)
    time.sleep(time_wait)
    e.run_experiment(e.probe_udp_RS)
    time.sleep(time_wait)

    return


def try_job():
    e = Experiment()
    print 'Try experiment '
    e.run_experiment(e.iperf_tcp_dw_RA)
    print 'DONE!'
    return


if __name__ == "__main__":

    schedule.every(10).minutes.do(experiment_suit)
    #schedule.every(1).minutes.do(try_job)

    indx = 0
    experiment_suit()
    indx += 1

    while True:
        print "Run next set ", indx
        schedule.run_pending()
        time.sleep(1)
        indx += 1
