from MapReduce.master import Master
import pickle
import time
import sys
def map_fn(data):
    input_string = data[1]
    mapped_data = list()
    input_string = input_string.strip()
    items = input_string.split()
    for word in items:
        word = ''.join(filter(str.isalnum, word))
        word = word.lower()
        mapped_data.append((word,1))
    return mapped_data

def reduce_fn(mapped_list):
    prev_word = None
    count = 1
    reduced_list = list()
    for item in mapped_list:
        if(item[0] == prev_word):
            count += 1 
        else:
            reduced_list.append((prev_word,count))
            count = 1
        prev_word = item[0]
    return reduced_list

def word_count(ip_address,num_mappers,mapper_ports,num_reducers,reducer_ports,input_files,output_file):
    ser_map = pickle.dumps(map_fn)
    ser_reduce = pickle.dumps(reduce_fn)
    master = Master(num_mappers,num_reducers,ip_address,mapper_ports,reducer_ports)
    start_time = time.time()
    master.run_mapred(input_files,ser_map,ser_reduce,output_file)
    print(f"Word count on {len(input_files)} documents completed in {(time.time() - start_time)} seconds. \nWritten to {output_file}")
if __name__ == '__main__':
    if(len(sys.argv)<8):
        raise Exception("Too few arguments")
    else:
        word_count(sys.argv[1],int(sys.argv[2]),eval(sys.argv[3]),int(sys.argv[4]),eval(sys.argv[5]),eval(sys.argv[6]),sys.argv[7])
    