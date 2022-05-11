import socket
hostname=socket.gethostname()   
local_host=socket.gethostbyname(hostname)  
#Eventual: 1, Linear: 2, Sequential: 3
STORE_TYPE = 1
#(ip address, port number)
LOAD_BALANCER_PORT = (local_host, 10001)

#Lenght of SERVER_PORTS and SERVER_IPS must equal SERVER_COUNT

SERVER_COUNT = 5

SERVER_PORTS = [(30001,40001),(30002,40002),(30003,40003),(30004,40004),(30005,40005)]

SERVER_IPS = [local_host,local_host,local_host,local_host,local_host]

GLOBAL_DELAY = 0
GLOBAL_BROADCAST_DELAY = 0
