import zmq
import pickle
import time
def reducer(ser_reduce,data,process_info):
    #Creates publisher socket to send data back to the master node
    context = zmq.Context()
    socket  = context.socket(zmq.PUB)
    socket.bind(process_info.getPort())

    #Loads the reduce function from its serialization
    reduce_func = pickle.loads(ser_reduce)

    #Examines all of the data provided and maps it
    reduced_data = reduce_func(data)

    #Increments vector clock and sends the mapped data to master until it is recieved
    process_info.increment_vector_clock()
    while(True):
        socket.send_pyobj((process_info,reduced_data))
        time.sleep(.5)