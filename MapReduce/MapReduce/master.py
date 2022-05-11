
from multiprocessing import Process
import zmq
from MapReduce.mapper import mapper
from MapReduce.reducer import reducer
import textwrap
import os

class ProcessInfo:
    def __init__(self,process_id, ip_address, port_number, vector_clock):
        self.process_id = process_id
        self.port_number = port_number
        self.vector_clock = vector_clock
        self.ip_address = ip_address
    
    #Takes this vector clock and syncronizes it with another
    def match_vector_clock(self,p2):
        for i in range(len(self.vector_clock)):
            self.vector_clock[i] = max(self.vector_clock[i],p2.vector_clock[i])

    #Increments the vector clock for this process
    def increment_vector_clock(self):
        self.vector_clock[self.process_id] += 1

    #Returns full port for this process
    def getPort(self):
        return f"tcp://{self.ip_address}:{self.port_number}"

class Master:

    def __init__(self,num_mappers,num_reducers,ip_address,map_ports,reduce_ports):
        #Checks to make sure an appropriate number of ports were provided
        if(len(map_ports)<num_mappers):
            raise Exception(f"Too few map ports provided, need {num_mappers} ports, provided {len(map_ports)}")
        if(len(reduce_ports)<num_reducers):
            raise Exception(f"Too few reduce ports provided, need {num_reducers} ports, provided {len(reduce_ports)}")
        self.num_mappers = num_mappers
        self.num_reducers = num_reducers
        self.map_ports = map_ports
        self.reduce_ports = reduce_ports
        self.ip_address = ip_address

        #ProcessInfo instace for the master node
        self.master_info = ProcessInfo(0,"","",[0 for i in range(num_mappers+num_reducers+1)])

    #Splits a list for the reducers
    def list_split(self, slist):
        split_list = list()
        chunk_size = int(len(slist)/(self.num_reducers)) + 1
        for i in range(0, len(slist), chunk_size):
            split_list.append(slist[i:i+chunk_size])
        return split_list    

    #Reads text files and splits them for the mappers
    def chunker(self,files):

        #All files are read and added to a list of strings
        read_files = list()
        file_num = 0
        for file in files:
            with open(f"MapReduce/data/{file}", encoding='utf-8') as f:
                input_string = f.read()
                read_files.append((file_num,input_string))
            file_num+=1  

        #Each string is chunked equally
        chunked_data_holder = list()
        for read_file in read_files:
            chunck_size = int(len(read_file[1])/(self.num_mappers))
            partial_chunked_data = textwrap.wrap(read_file[1],width = chunck_size,max_lines = self.num_mappers)
            chunked_data_holder.append(partial_chunked_data)

        #Corrosponding chunks are added together to ensure balenced chunking
        chunked_data = list()
        for i in range(self.num_mappers):
            chunked_data.append([(j,chunked_data_holder[j][i]) for j in range(len(chunked_data_holder))])
        return chunked_data

    #Sorts the mapped data
    def shuffle(self,list):
        def compare(item):
            return item[0]
        list.sort(key=compare)
        return list

    def run_mapred(self,input_data,ser_map,ser_reduce,output_location):
        #Data is read and chunked
        chunked_strings = self.chunker(input_data)

        #Subscriber socket is intilized
        processes = list()
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        
        #All mappers are started
        for i in range(self.num_mappers):
            port_number = str(self.map_ports[i])
            self.master_info.increment_vector_clock()
            process_info = ProcessInfo(i+1,self.ip_address,port_number,self.master_info.vector_clock)
            process = Process(target=mapper,args = (ser_map,chunked_strings[i], process_info,))
            processes.append(process)
            #Subscriber listens for contact from process
            socket.connect(process_info.getPort())
            process.start() 
        socket.subscribe("")

        #Loop listens for data from map cluster
        mapped_data = list()
        message_count = 0
        while(message_count<self.num_mappers):
            message = socket.recv_pyobj()
            process_info = message[0]
            data = message[1]
            #Listens for each process at least once
            if self.master_info.vector_clock[process_info.process_id] == 0:
                mapped_data += data
                self.master_info.match_vector_clock(process_info)
                message_count += 1
            #Processes are terminated when message is recieved
            processes[process_info.process_id-1].terminate()

        #Data is sorted and chunked
        shuffled_mapped_data = self.shuffle(mapped_data)
        chunked_mapped_data = list(self.list_split(shuffled_mapped_data))

        #All reducers are started
        processes = list()
        for i in range(self.num_reducers):
            port_number = str(self.reduce_ports[i])
            process_info = ProcessInfo(self.num_mappers+i+1,self.ip_address,port_number,self.master_info.vector_clock)
            process = Process(target = reducer,args=(ser_reduce,chunked_mapped_data[i],process_info,))
            processes.append(process)
            #Subscriber listens for contact from process
            socket.connect(process_info.getPort())
            process.start()  
        socket.subscribe("")
    
        #Loop listens for data from reduce cluster
        output_data = list()
        message_count = 0   
        while(message_count<self.num_reducers):
            message = socket.recv_pyobj()
            process_info = message[0]
            data = message[1]
            #Listens for each process at least once
            if self.master_info.vector_clock[process_info.process_id] == 0:
                output_data += data
                self.master_info.match_vector_clock(process_info)
                message_count += 1
            #Process is terminated when message is recieved
            processes[process_info.process_id-self.num_mappers-1].terminate()

        #Ouput data is formated
        output_string = '\n'.join(str(item) for item in output_data)

        #Output data is written to output file
        path = "MapReduce/bin/"
        file = open(os.path.join(path,output_location),'w+')
        file.write(output_string)
        file.close()
        socket.close()

