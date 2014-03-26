# DO NOT CHANGE THESE VALUES
#SERVER_ADDRESS = '130.207.97.240'
SERVER_ADDRESS = '192.168.20.1'
SERVER_INTERFACE_NAME = 'eth1'
CONTROL_PORT = 12345
MSG_SIZE = 1024
experiment_timeout = 15
passive_timeout = 5
#collect passive trace + tcpdump without active probe traffic for 2 mins
calibrate_timeout = 120

# UPDATE THE FOLLOWING VALUES
ROUTER_ADDRESS_LOCAL = '192.168.10.1'
ROUTER_USER = 'root'
#ROUTER_PASS = 'bismark123'
ROUTER_PASS = 'passw0rd'
ROUTER_ADDRESS_GLOBAL = '192.168.1.2'
#ROUTER_ADDRESS_GLOBAL = '50.167.212.31'
CLIENT_ADDRESS = '192.168.10.184'
#CLIENT_ADDRESS = '192.168.1.158'
CLIENT_WIRELESS_INTERFACE_NAME = 'wlan0'
#CLIENT_WIRELESS_INTERFACE_NAME = 'wlan1' #if 5 GHz
ROUTER_WIRELESS_INTERFACE_NAME = 'wlan0'
#ROUTER_WIRELESS_INTERFACE_NAME = 'wlan1' #if 5 GHz
