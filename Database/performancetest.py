from datetime import datetime
from unicodedata import name
from data_classes.command import Command, SetCommand, GetCommand
import random
from server_cluster import configure
from data_classes.ProcessInfo import ProcessInfo
from client import auto_client
from multiprocessing import Process
import time
commands = []
size = 15
client_count = 5
keys = ['a','b','c','d','e','f','g']
for i in range(size):
    curr_dt = datetime.now()
    randint = random.randint(0,6)
    commands.append(GetCommand(keys[randint],curr_dt.timestamp()))

for i in range(size):
    curr_dt = datetime.now()
    randint = random.randint(0,6)
    commands.append(SetCommand(keys[randint],i,curr_dt.timestamp()))

clients = []
for i in range(client_count):
    random.shuffle(commands)
    balancer_info = ProcessInfo(i,configure.LOAD_BALANCER_PORT[0],configure.LOAD_BALANCER_PORT[1])
    clients.append(Process(target=auto_client, args=(balancer_info,commands,)))
    
if __name__ == '__main__':
    start_time = time.time()
    for client in clients:
        client.start()
    for client in clients:
        client.join()
    print(f"{client_count*size} gets and {client_count*size} sets done from {client_count} clients in {time.time()-start_time} seconds using configuration {configure.STORE_TYPE} with {configure.SERVER_COUNT} servers")


    
    
