import subprocess
import socket
hostname=socket.gethostname()   
local_host=socket.gethostbyname(hostname)  


#Config parameters
func = "word_count.py"
ip_addr = local_host
num_mappers = 1
map_ports = [1000]
num_reducers = 1
reduce_ports = [2000]
files = ["gg.txt"]
output_location = "output.txt"

subprocess.run(args=("py",func,ip_addr,str(num_mappers),str(map_ports),str(num_reducers),str(reduce_ports),str(files),output_location,))