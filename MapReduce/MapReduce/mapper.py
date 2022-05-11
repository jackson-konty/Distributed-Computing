import zmq
import pickle
import time
def mapper(ser_map, data, process_info):
    #Creates publisher socket to send data back to the master node
    context = zmq.Context()
    socket  = context.socket(zmq.PUB)
    socket.bind(process_info.getPort())

    #Loads the map function from its serialization
    map_func = pickle.loads(ser_map)

    #Examines all of the data provided and maps it
    mapped_data = list()
    for sub_data in data:
        mapped_data.extend(map_func(sub_data))

    #Increments vector clock and sends the mapped data to master until it is recieved
    process_info.increment_vector_clock()
    while(True):
        socket.send_pyobj((process_info,mapped_data))
        time.sleep(.5)
    
    


    