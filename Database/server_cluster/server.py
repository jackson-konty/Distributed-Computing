
from server_cluster.database.sql import KVstore
from parse import *
import zmq
from data_classes.ProcessInfo import ServerInfo
from data_classes.command import *
import time
import server_cluster.configure
delay = server_cluster.configure.GLOBAL_DELAY
broadcast_delay = server_cluster.configure.GLOBAL_BROADCAST_DELAY

def server_eventual(server_info:ServerInfo,servers: list([ServerInfo])):
    '''This function creates a server that listens for requests from the load balancer and other servers.
    
    Parameters
    ----------
    server_info : ServerInfo
        ServerInfo = ServerInfo(process_id,client_port,server_port)
    servers : list([ServerInfo])
        list([ServerInfo])
    
    '''
    file = f"server{server_info.process_id}.db"
    kv = KVstore(db_file=repr(file))
    context =  zmq.Context()
    #Set up socket that replies to the load balancer
    client_reply_socket = context.socket(zmq.REP)
    client_reply_socket.bind(server_info.getClientPort())
    
    #Set up the socket the communicates with the adjacent server Node
    server_pub_socket = context.socket(zmq.PUB)
    server_pub_socket.bind(server_info.getServerPort())
    
    #Sets up socket to recieve from adjacent server Node
    server_sub_socket = context.socket(zmq.SUB)
    for server in servers:
        server_sub_socket.connect(server.getServerPort())
    server_sub_socket.subscribe("")

    #Establlishes poller and registers all sockets
    poller = zmq.Poller()
    poller.register(client_reply_socket,zmq.POLLIN)
    poller.register(server_sub_socket, zmq.POLLIN)
    print(f"server {server_info.process_id} ready")
    
    while True:
        socks = dict(poller.poll())
        if client_reply_socket in socks and socks[client_reply_socket] == zmq.POLLIN:
            command : Command = client_reply_socket.recv_pyobj()
            if command:      
                if command.getType() == CommandType.SET:
                    if kv.addPair(command.getKey(),command.getValue(),command.getTimestamp()):
                        # Printing the process id of the server and the string "Client value stored"
                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj("STORED\r\n")
                        #For testing, simulates long request handling
                        #time.sleep(3)
                        #Simulate latency
                        time.sleep(broadcast_delay)
                        server_pub_socket.send_pyobj(command)
                    else:
                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj("NOT-STORED\r\n")
                elif command.getType() == CommandType.GET:
                    res = kv.getValue(command.getKey())
                    if res:
                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj(res.toString())
                    else:
                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj("END\r\n")
        if server_sub_socket in socks and socks[server_sub_socket] == zmq.POLLIN:
            command = server_sub_socket.recv_pyobj()
            if command:
                kv.addPair(command.getKey(),command.getValue(),command.getTimestamp())


            
            
def server_linear(server_info:ServerInfo,servers: list([ServerInfo])):
    '''This function creates a server that listens for requests from the load balancer and other servers.
    
    Parameters
    ----------
    server_info : ServerInfo
        ServerInfo = ServerInfo(process_id,client_port,server_port)
    servers : list([ServerInfo])
        list([ServerInfo])
    
    '''
    file = f"server{server_info.process_id}.db"
    kv = KVstore(db_file=repr(file))
    context =  zmq.Context()
    #Set up socket that replies to the load balancer
    client_reply_socket = context.socket(zmq.REP)
    client_reply_socket.bind(server_info.getClientPort())
    
    #Set up the socket the communicates with the adjacent server Node
    server_pub_socket = context.socket(zmq.PUB)
    server_pub_socket.bind(server_info.getServerPort())
    
    #Sets up socket to recieve from adjacent server Node
    server_sub_socket = context.socket(zmq.SUB)
    server_confirm_socket = context.socket(zmq.SUB)
    for server in servers:
        server_confirm_socket.connect(server.getServerPort())
        server_sub_socket.connect(server.getServerPort())
    server_sub_socket.subscribe("")
    server_confirm_socket.subscribe("")

    #Establlishes poller and registers all sockets
    poller = zmq.Poller()
    poller.register(client_reply_socket,zmq.POLLIN)
    poller.register(server_sub_socket, zmq.POLLIN)
    print(f"server {server_info.process_id} ready")
    
    while True:
        socks = dict(poller.poll())
        if client_reply_socket in socks and socks[client_reply_socket] == zmq.POLLIN:
            command : Command = client_reply_socket.recv_pyobj()
            if command:      
                if command.getType() == CommandType.SET:
                    if kv.addPair(command.getKey(),command.getValue(),command.getTimestamp()):
                        #Simulate latency
                        time.sleep(broadcast_delay)
                        # This is the code that is used to confirm that the message has been received by all the servers.
                        server_pub_socket.send_pyobj(command)
                        count = 0
                        while count < len(servers)-1:
                            message = server_confirm_socket.recv_pyobj()
                            if(message == "confirm"):
                                count += 1

                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj("STORED\r\n")
                    else:
                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj("NOT-STORED\r\n")
                elif command.getType() == CommandType.GET:
                    res = kv.getValue(command.getKey())
                    if res:
                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj(res.toString())
                    else:
                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj("END\r\n")
        if server_sub_socket in socks and socks[server_sub_socket] == zmq.POLLIN:
            command = server_sub_socket.recv_pyobj()
            if type(command) != str:
                kv.addPair(command.getKey(),command.getValue(),command.getTimestamp())
                #For testing, simulates long request handling
                time.sleep(delay)
                server_pub_socket.send_pyobj("confirm")

            
def server_sequential(server_info:ServerInfo,servers: list([ServerInfo])):
    '''This function creates a server that listens for requests from the load balancer and other servers.
    
    Parameters
    ----------
    server_info : ServerInfo
        ServerInfo = ServerInfo(process_id,client_port,server_port)
    servers : list([ServerInfo])
        list([ServerInfo])
    
    '''
    file = f"server{server_info.process_id}.db"
    kv = KVstore(db_file=repr(file))
    context =  zmq.Context()
    #Set up socket that replies to the load balancer
    client_reply_socket = context.socket(zmq.REP)
    client_reply_socket.bind(server_info.getClientPort())
    
    #Set up the socket the communicates with the adjacent server Node
    server_pub_socket = context.socket(zmq.PUB)
    server_pub_socket.bind(server_info.getServerPort())
    
    #Sets up socket to recieve from adjacent server Node
    server_sub_socket = context.socket(zmq.SUB)
    server_confirm_socket = context.socket(zmq.SUB)
    for server in servers:
        server_confirm_socket.connect(server.getServerPort())
        server_sub_socket.connect(server.getServerPort())
    server_sub_socket.subscribe("")
    server_confirm_socket.subscribe("")

    #Establlishes poller and registers all sockets
    poller = zmq.Poller()
    poller.register(client_reply_socket,zmq.POLLIN)
    poller.register(server_sub_socket, zmq.POLLIN)
    print(f"server {server_info.process_id} ready")
    
    while True:
        socks = dict(poller.poll())
        if client_reply_socket in socks and socks[client_reply_socket] == zmq.POLLIN:
            command : Command = client_reply_socket.recv_pyobj()
            if command:      
                if command.getType() == CommandType.SET:
                    if kv.addPair(command.getKey(),command.getValue(),command.getTimestamp()):
                        # Printing the process id of the server and the string "Client value stored"
                        #For testing, simulates long request handling
                        #time.sleep(3)
                        #Simulate latency
                        time.sleep(broadcast_delay)
                        server_pub_socket.send_pyobj(command)
                        # This is the code that is used to confirm that the message has been received by all the servers.
                        count = 0
                        while count < len(servers)-1:
                            message = server_confirm_socket.recv_pyobj()
                            if(message == f"confirm{command.getPid()}"):
                                count += 1
                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj(("STORED\r\n",command.getPid()))
                    else:
                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj(("NOT-STORED\r\n",command.getPid()))
                elif command.getType() == CommandType.GET:
                    res = kv.getValue(command.getKey())
                    if res:
                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj((res.toString(),command.getPid()))
                    else:
                        #Simulate latency
                        time.sleep(delay)
                        client_reply_socket.send_pyobj(("END\r\n",command.getPid()))
        if server_sub_socket in socks and socks[server_sub_socket] == zmq.POLLIN:
            command = server_sub_socket.recv_pyobj()
            if type(command) != str:
                kv.addPair(command.getKey(),command.getValue(),command.getTimestamp())
                #For testing, simulates long request handling
                #time.sleep(3)
                #Simulate latency
                time.sleep(delay)
                server_pub_socket.send_pyobj(f"confirm{command.getPid()}")
