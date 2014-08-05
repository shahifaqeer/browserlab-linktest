browserlab-linktest
===================
1. Clone repository
2. Install *Required Tools (Dependencies)*
3. *Update constants.py*
4. run client.py as sudo
  sudo python client.py
  
Summary
This script performs an *experiment suit* (see below) every 10 minutes.
It creates a folder /tmp/browserlab where all experiment traces are collected before copying them to the server.
At the moment, traces are not deleted from /tmp/browserlab/
Note: We refer to the wireless client device as A, gateway as R, and server as S


			(home)	      (gateway)	     (Internet)	   (server @ GT)
	(wireless device) A - - -- - - - - R ------------------------- S
	   [Private address space]      [Public IP]	        [130.207.97.240]

				Inside	  v/s      Outside

			     Fig 1: Real Home Network Topology

Collected traces
- iperf (10 sec tests between AR, AS, RS)
- fping (AR, AS, RA, RS)
- tcpdump (at A and R during test)
- radiotap headers (at wireless interfaces of both A and R during test)

Experiments
-----------

- calibrate: passively collect tcpdump + radiotap headers on A and R for 120 sec without any active probing traffic
- no traffic: only pings between A, R, S for 10 sec at 100 ms each => 100 ping readings + tcpdump and radiotap
- iperf (client, server): pings + tcpdump + radiotap + tcp iperf between client and server (A, R, or S)
- probe (client, server): pings + tcpdump + radiotap + udp probe between client and server (A, R, or S)

For more details about the experiment and results see: https://docs.google.com/document/d/1kB8c66Kw5TNwpFnXjMKmZbMzs8R3VRwe5whlTB9QlFU

Required Tools (Dependencies)
-----------------------------

ROUTER
- udpprobe: opkg install http://riverside.noise.gatech.edu:8080/udpprobe_2014-03-09_ar71xx.ipk
- sysstats: opkg install http://downloads.openwrt.org/attitude_adjustment/12.09/ar71xx/generic/packages/sysstat_9.0.6-1_ar71xx.ipk
- iperf3: opkg install http://cmon.lip6.fr/~apietila/tma2014/router/iperf3_2013-12-11_ar71xx.ipk

If the router is not bismark, you will also need
- iperf: opkg install http://cmon.lip6.fr/~apietila/tma2014/router/iperf_2.0.5-1_ar71xx.ipk
- fping: opkg install fping

CLIENT
- sshpass: sudo apt-get install sshpass
- fping: https://github.com/shahifaqeer/fping (follow installation steps in README)
- iperf3 [iperf not needed]: https://github.com/esnet/iperf
	- ./configure
	- make
	- make install
- iperf reverse (maybe): https://github.com/shahifaqeer/iperf (replace normal iperf either by uninstalling first or using 'install' command)
- udpprobe: https://github.com/shahifaqeer/shaperprobe
	- make shaperprobe/udpprobe/linux/ and shaperprobe/udpprobeserver/ (I haven't fixed the osx or windows version yet)
	- in these folders run 
  		sudo install udpprober /usr/local/bin/
  		sudo install udpprobeserver /usr/local/bin/ 
	- (or simply add these directory to your PATH)
- paramiko (python module): sudo pip install paramiko
- sar: sudo apt-get install sysstat

Update constants.py
-------------------

The following entries will need to be updated manually for now (defaults provided).
Basically this includes IP addresses, router information, and interface names

- ROUTER_ADDRESS_LOCAL = '192.168.1.1'
- ROUTER_USER = 'root'
- ROUTER_PASS = 'bismark123'
- ROUTER_ADDRESS_GLOBAL =  '50.167.212.31'
- CLIENT_ADDRESS = '192.168.1.153'
- CLIENT_WIRELESS_INTERFACE_NAME = 'wlan0'  # on debian
- ROUTER_WIRELESS_INTERFACE_NAME = 'wlan0'  # bismark 2.4 GHz interface name
- INIT_ACCESS_RATE = 100 #Mbps by default

Make sure that you enter the right interface name (wlan0/wlan1) for both client and router based on the channel you're on.
