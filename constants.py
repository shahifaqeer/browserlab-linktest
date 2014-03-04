CONTROL_PORT = 12345
MSG_SIZE = 1024

experiment_timeout =  10
#collect passive trace + tcpdump without active probe traffic for 2 mins
calibrate_timeout = 120
transfer_timeout =  experiment_timeout + 2
ROUTER_ADDRESS_LOCAL = '192.168.1.1'
ROUTER_USER = 'root'
ROUTER_PASS = 'bismark123'
ROUTER_ADDRESS_GLOBAL =  '50.167.212.31'
SERVER_ADDRESS = '130.207.97.240'
CLIENT_ADDRESS = '192.168.1.153'
CLIENT_WIRELESS_INTERFACE_NAME = 'eth1'
#CLIENT_WIRELESS_INTERFACE_NAME = 'wlan1' #if 5 GHz
ROUTER_WIRELESS_INTERFACE_NAME = 'wlan0'
#ROUTER_WIRELESS_INTERFACE_NAME = 'wlan1' #if 5 GHz
