from data_classes.command import *
from data_classes.ProcessInfo import ProcessInfo, ServerInfo
import zmq
import time
import server_cluster.configure
delay = server_cluster.configure.GLOBAL_DELAY
def balancer_eventual(info:ProcessInfo, servers: list[ServerInfo]):
    '''It receives a command from the client, sends it to the server, receives a response from the server,
    and sends the response back to the client
    
    Parameters
    ----------
    info : ProcessInfo
    servers : list[ServerInfo]
    
    '''
    context =  zmq.Context()
    server_socket = context.socket(zmq.REQ)
    for server in servers:
        server_socket.connect(server.getClientPort())
    client_socket = context.socket(zmq.REP)
    client_socket.bind(info.getPort())
    poller = zmq.Poller()
    poller.register(server_socket,zmq.POLLIN)
    poller.register(client_socket,zmq.POLLIN)
    print("Load balancer ready")
    while True:
        socks = dict(poller.poll())
        if client_socket in socks and socks[client_socket] == zmq.POLLIN:
            command:Command = client_socket.recv_pyobj()
            #Simulate latency
            time.sleep(delay)
            server_socket.send_pyobj(command)

        elif server_socket in socks and socks[server_socket] == zmq.POLLIN:
            response = server_socket.recv_pyobj()
            #Simulate latency
            time.sleep(delay)
            client_socket.send_pyobj(response)

def commandSort(command:Command):
    '''It takes a command object and returns the timestamp of that command
    
    Parameters
    ----------
    command : Command
        The command object that is being sorted
    
    Returns
    -------
        The timestamp of the command
    
    '''
    return command.getTimestamp()
            
def balancer_linear(info:ProcessInfo, servers: list[ServerInfo]):
    '''The load balancer receives a command from the client, and sends it to the server. When the server
    responds, the load balancer sends the response back to the client
    
    Parameters
    ----------
    info : ProcessInfo
        This is the information about the load balancer.
    servers : list[ServerInfo]
        list[ServerInfo]
    
    '''
    command_queue = list()
    context =  zmq.Context()
    server_socket = context.socket(zmq.REQ)
    for server in servers:
        server_socket.connect(server.getClientPort())
    client_socket = context.socket(zmq.REP)
    client_socket.bind(info.getPort())
    poller = zmq.Poller()
    poller.register(server_socket,zmq.POLLIN)
    poller.register(client_socket,zmq.POLLIN)
    print("Load balancer ready")
    while True:
        socks = dict(poller.poll())
        if client_socket in socks and socks[client_socket] == zmq.POLLIN:
            command:Command = client_socket.recv_pyobj()
            if(len(command_queue) == 0):
                #Simulate latency
                time.sleep(delay)
                server_socket.send_pyobj(command)
            command_queue.append(command)
    
        elif server_socket in socks and socks[server_socket] == zmq.POLLIN:
            response = server_socket.recv_pyobj()
            if(len(command_queue)>0):
                command_queue.pop(0)
            if(len(command_queue)>0):
                command_queue.sort(reverse=True, key = commandSort)
                #Simulate latency
                time.sleep(delay)
                server_socket.send_pyobj(command_queue[0])
            #Simulate latency
            time.sleep(delay)
            client_socket.send_pyobj(response)
            
def balancer_sequential(info:ProcessInfo, servers: list[ServerInfo]):
    command_queues = dict()
    context =  zmq.Context()
    server_socket = context.socket(zmq.REQ)
    for server in servers:
        server_socket.connect(server.getClientPort())
    client_socket = context.socket(zmq.REP)
    client_socket.bind(info.getPort())
    poller = zmq.Poller()
    poller.register(server_socket,zmq.POLLIN)
    poller.register(client_socket,zmq.POLLIN)
    print("Load balancer ready")
    while True:
        socks = dict(poller.poll())
        if client_socket in socks and socks[client_socket] == zmq.POLLIN:
            command:Command = client_socket.recv_pyobj()
            if not command.getPid() in command_queues.keys():
                command_queues[command.getPid()] = []
            if(len(command_queues[command.getPid()]) == 0):
                #Simulate latency
                time.sleep(delay)
                server_socket.send_pyobj(command)
            command_queues[command.getPid()].append(command)
    
        elif server_socket in socks and socks[server_socket] == zmq.POLLIN:
            response = server_socket.recv_pyobj()
            if(len(command_queues[response[1]])>0):
                command_queues[response[1]].pop(0)
            if(len(command_queues[response[1]])>0):
                command_queues[response[1]].sort(reverse=True, key = commandSort)
                #Simulate latency
                time.sleep(delay)
                server_socket.send_pyobj(command_queues[response[1]][0])
            #Simulate latency
            time.sleep(delay)
            client_socket.send_pyobj(response[0])
