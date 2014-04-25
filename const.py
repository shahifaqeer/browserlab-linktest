# DO NOT CHANGE THESE VALUES
SERVER_ADDRESS = '192.168.20.1'
SERVER_INTERFACE_NAME = 'eth0'
CONTROL_PORT = 12345
MSG_SIZE = 1024
EXPERIMENT_TIMEOUT = 10
PASSIVE_TIMEOUT = 5
#collect passive trace + tcpdump without active probe traffic for 2 mins
CALIBRATE_TIMEOUT = 120
PING_SIZE = '1400'

# UPDATE THE FOLLOWING VALUES
ROUTER_USER = 'root'
ROUTER_PASS = 'passw0rd'
ROUTER_ADDRESS_GLOBAL = '192.168.1.2'
ROUTER_ADDRESS_LOCAL = '192.168.10.1'
CLIENT_ADDRESS = '192.168.10.184'
CLIENT_WIRELESS_INTERFACE_NAME = 'wlan0'
#CLIENT_WIRELESS_INTERFACE_NAME = 'wlan1' #if 5 GHz ?
ROUTER_WIRELESS_INTERFACE_NAME = 'wlan0'
#ROUTER_WIRELESS_INTERFACE_NAME = 'wlan1' #if 5 GHz
ROUTER_ADDRESS_PINGS = '192.168.1.1'

GENERIC_WIRELESS_INTERFACE_NAME = "wlan"

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
