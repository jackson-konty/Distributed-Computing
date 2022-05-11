from multiprocessing import Process
from server_cluster.server import server_eventual, server_linear, server_sequential
from data_classes.ProcessInfo import ServerInfo,ProcessInfo
from server_cluster.loadbalancer import balancer_eventual, balancer_linear, balancer_sequential
import socket
from server_cluster import configure
hostname=socket.gethostname()
local_host=socket.gethostbyname(hostname)

server_type = None
balancer_type = None
#Type of server and balancer, must match
if(configure.STORE_TYPE == 1):
    server_type = server_eventual
    balancer_type = balancer_eventual

elif(configure.STORE_TYPE == 2):
    server_type = server_linear
    balancer_type = balancer_linear
elif(configure.STORE_TYPE == 3):
    server_type = server_sequential
    balancer_type = balancer_sequential
#Each server needs two sockets and an ip_address. Can adjust either


server_info= list()
for i in range(configure.SERVER_COUNT):
    server_info.append(ServerInfo(i,configure.SERVER_IPS[i],configure.SERVER_PORTS[i][0],configure.SERVER_PORTS[i][1]))

servers = []
for i in range(configure.SERVER_COUNT):
    servers.append(Process(target = server_type,args=(server_info[i],server_info,)))
    

balancerInfo = ProcessInfo(0,configure.LOAD_BALANCER_PORT[0],configure.LOAD_BALANCER_PORT[1])
load_balancer = Process(target = balancer_type, args = (balancerInfo,server_info,))

if __name__ == '__main__':
    for server in servers:
        server.start()
    load_balancer.start()
    for server in servers:
        server.join()
    load_balancer.join()
