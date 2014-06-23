# DO NOT CHANGE THESE VALUES
CONTROL_PORT = 12345
MSG_SIZE = 1024
PASSIVE_TIMEOUT = 5
#collect passive trace + tcpdump without active probe traffic for 2 mins
CALIBRATE_TIMEOUT = 120
PING_SIZE = '1400'
PERF_PORT = '5001'

# Configuration and measurement options
EXPERIMENT_TIMEOUT = 5      # test time for tcp and udp tests
COLLECT_tcp = 1
COLLECT_udp = 1
COLLECT_udp_blast = 0
COLLECT_tcpdump = 1         # tcpdump is messing things up so don't collect at the moment
USE_IPERF3 = 1
USE_PARALLEL_TCP = 0        # in case we need to test parallel
TCP_PARALLEL_STREAMS = 10   # in case we need to test parallel
INIT_HOME_RATE = 100        # Mbps threshold for wireless iperf udp -b
INIT_ACCESS_RATE = 100      # Mbps fore access link iperf udp -b
INIT_BLAST_RATE = 150       # Mbps fore access link iperf udp -b
PROBE_TIMEOUT = 25          # seconds for shaperprobe udp
USE_IPERF_TIMEOUT = 1       # use -t <EXPERIMENT_TIMEOUT> instead of -n
NUM_BITS_TO_SEND = '100M'   # use -b <NUM_BITS_TO_SEND> instead of -t
TMP_BROWSERLAB_PATH = '$HOME/tmp/browserlab/'
TMP_DATA_PATH = '$HOME/browserlab/'
DATA_SERVER_PATH = 'browserlab@130.207.97.240:'

# UPDATE THE FOLLOWING VALUES
ROUTER_USER = 'root'
CLIENT_WIRELESS_INTERFACE_NAME = 'wlan0' #'wlan0'
#CLIENT_WIRELESS_INTERFACE_NAME = 'wlan1' #if 5 GHz ?
ROUTER_WIRELESS_INTERFACE_NAME = 'wlan0'
#ROUTER_WIRELESS_INTERFACE_NAME = 'wlan1' #if 5 GHz
ROUTER_ADDRESS_PINGS = ''
GENERIC_WIRELESS_INTERFACE_NAME = "wlan"

# Testbed settings
#SERVER_ADDRESS = '192.168.20.1'     #testbed
#SERVER_INTERFACE_NAME = 'eth1'      #testbed
#ROUTER_PASS = 'passw0rd'            #testbed
#ROUTER_ADDRESS_GLOBAL = '192.168.1.2'
#ROUTER_ADDRESS_LOCAL = '192.168.10.1'
#CLIENT_ADDRESS = '192.168.10.184'

# Real settings
SERVER_ADDRESS = '130.207.97.240'
SERVER_INTERFACE_NAME = 'eth0'
ROUTER_PASS = 'bismark123'
ROUTER_ADDRESS_GLOBAL = '50.167.212.31'
ROUTER_ADDRESS_LOCAL = '192.168.142.1'
CLIENT_ADDRESS = '192.168.142.183'

# ---------------------------------------------------------

# DIRECT CONNECTION TO MODEM: NO ROUTER
#ROUTER_USER = 'gtnoise'
#ROUTER_PASS = 'gtnoise'
#ROUTER_ADDRESS_GLOBAL = '76.97.4.242'
#ROUTER_ADDRESS_LOCAL = '76.97.4.242'
#CLIENT_ADDRESS = '76.97.4.242'
#CLIENT_WIRELESS_INTERFACE_NAME = 'eth0'
#ROUTER_WIRELESS_INTERFACE_NAME = 'eth0'

# WIRED CONNECTION TO ROUTER
#ROUTER_USER = 'root'
#ROUTER_PASS = 'passw0rd'
#ROUTER_ADDRESS_GLOBAL = '50.167.212.31'
#ROUTER_ADDRESS_LOCAL = '192.168.1.1'
#CLIENT_ADDRESS = '192.168.1.2'
#CLIENT_WIRELESS_INTERFACE_NAME = 'eth0'
#ROUTER_WIRELESS_INTERFACE_NAME = 'eth0'

# NON COOP MEASUREMENT
#ROUTER_USER = 'gtnoise'
#ROUTER_PASS = 'gtnoise'
#ROUTER_ADDRESS_GLOBAL = '50.167.212.31'
#ROUTER_ADDRESS_PINGS = '192.168.1.1'
#ROUTER_ADDRESS_LOCAL = '192.168.1.184'
#CLIENT_ADDRESS = '192.168.1.158'
#CLIENT_WIRELESS_INTERFACE_NAME = 'wlan0'
#ROUTER_WIRELESS_INTERFACE_NAME = 'wlan0'
