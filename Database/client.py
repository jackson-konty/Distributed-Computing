
import zmq
from data_classes.ProcessInfo import ProcessInfo
from parse import *
from data_classes.command import *
from datetime import datetime
import time
import random
import socket
from server_cluster import configure
import sys
def client(balancer_info:ProcessInfo):
    '''The client function creates a socket that connects to the load balancer, then it creates a poller
    that polls the socket for a response from the load balancer. If the poller receives a response, it
    prints the response. If the poller times out, it prints a timeout message
    
    Parameters
    ----------
    balancer_info : ProcessInfo
        This is the process info of the load balancer.
    
    '''
    # Create socket that can send messages to the load balancer
    context =  zmq.Context()
    balancer_socket = context.socket(zmq.REQ)
    balancer_socket.connect(balancer_info.getPort())

    #Register sockets in a poller
    poller = zmq.Poller()
    poller.register(balancer_socket,zmq.POLLIN)
    print("Enter c to close")

    reconnect = False
    while True:
        raw_command = input("get or set commmand: ")
        if raw_command.lower() == 'c':
            break
        start_time = time.time()
        if(reconnect):
            context =  zmq.Context()
            balancer_socket = context.socket(zmq.REQ)
            balancer_socket.connect(balancer_info.getPort())
            poller = zmq.Poller()
            poller.register(balancer_socket,zmq.POLLIN)
            reconnect = False
        command_list = cleanMessage(raw_command)
        command = None
        if command_list:
            curr_dt = datetime.now()
            timestamp = round(curr_dt.timestamp())
            if isSet(command_list[0]):
                command = SetCommand(command_list[1],' '.join(command_list[2:]),int(timestamp))
            elif isGet(command_list[0]):
                command = GetCommand(command_list[1],int(timestamp))
        if(command):
            command.attach_pid(balancer_info.process_id)
            balancer_socket.send_pyobj(command)
            print(f"REQUEST SENT: {curr_dt}")
            socks = dict(poller.poll(10000))
            if balancer_socket in socks and socks[balancer_socket] == zmq.POLLIN:
                response = balancer_socket.recv_pyobj()
                print(f"{'-'*5} {time.time()-start_time} seconds {'-'*5}")
                print(f'FROM SERVER:\n\r{response}')
            else:
                print(f'TIMEOUT')
                reconnect = True
        else:
            print("INVALID COMMMAND\n\r")
    balancer_socket.close()
    
def auto_client(balancer_info:ProcessInfo,commands:list([Command])):
    '''It sends a list of commands to the load balancer and prints the response
    
    Parameters
    ----------
    balancer_info : ProcessInfo
        This is the ProcessInfo object that contains the information about the load balancer.
    commands : list([Command])
        list([Command])
    
    '''
    # Create socket that can send messages to the load balancer
    context =  zmq.Context()
    balancer_socket = context.socket(zmq.REQ)
    balancer_socket.connect(balancer_info.getPort())
    #Register sockets in a poller
    poller = zmq.Poller()
    poller.register(balancer_socket,zmq.POLLIN)
    reconnect = False
    for command in commands:
        start_time = time.time()
        if(reconnect):
            context =  zmq.Context()
            balancer_socket = context.socket(zmq.REQ)
            balancer_socket.connect(balancer_info.getPort())
            poller = zmq.Poller()
            poller.register(balancer_socket,zmq.POLLIN)
            reconnect = False
        curr_dt = datetime.now()
        if(command):
            command.attach_pid(balancer_info.process_id)
            balancer_socket.send_pyobj(command)
            print(f"REQUEST SENT: {curr_dt}")
            socks = dict(poller.poll(30000))
            if balancer_socket in socks and socks[balancer_socket] == zmq.POLLIN:
                response = balancer_socket.recv_pyobj()
                print(f"{'-'*5} {time.time()-start_time} seconds {'-'*5}")
                print(f'FROM SERVER:\n\r{response}')
            else:
                print(f'TIMEOUT')
                reconnect = True
        else:
            print("INVALID COMMMAND\n\r")
    balancer_socket.close()
    

if __name__ == '__main__':
    balencer_info = ProcessInfo(sys.argv[1],configure.LOAD_BALANCER_PORT[0],configure.LOAD_BALANCER_PORT[1])
    client(balencer_info)
    