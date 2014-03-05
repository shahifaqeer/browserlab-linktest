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
		    [Private address space] [Public IP]	        [130.207.97.240]

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
- udpprobe: opkg install http://riverside.noise.gatech.edu:8080/udpprobe_2013-12-11_ar71xx.ipk

If the router is not bismark, you will also need
- iperf: opkg install iperf
- fping: opkg install fping

CLIENT
- sshpass: sudo apt-get install sshpass
- fping: https://github.com/shahifaqeer/fping (follow installation steps in README)
- iperf reverse: https://github.com/shahifaqeer/iperf (replace normal iperf either by uninstalling first or using 'install' command)
- udpprobe: https://github.com/shahifaqeer/shaperprobe
	- make shaperprobe/shaperprobe/linux/ and shaperprobe/shaperprobeserver/ (I haven't fixed the osx or windows version yet) and give it execution permissions
		sudo chmod 777 udpprober
	- in these folders run 
  		sudo install -D -t /usr/local/bin/ udpprober
  		sudo install -D -t /usr/local/bin/ udpprobeserver
- schedule (python module): sudo pip install schedule
- paramiko (python module): sudo pip install paramiko

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

Make sure that you enter the right interface name (wlan0/wlan1) based on the channel you're on.
