import subprocess
import socket 
hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname)  
func = input("Enter the function you would like to use (word_count or inverted_index): ")
func = f"{func}.py"
files = input("Enter the files that you would like to read (e.g. gg.txt ts.txt): ").split()
output_location = input("Enter your desired output destination (e.g. output.txt): ")
ip_address = input("Enter IP Adress (leave empty for local host): ")
num_mappers = int(input("Enter your desired number of map clusters: "))

if(ip_address==""):
    ip_address = IPAddr
map_ports = []
for i in range(num_mappers):
    map_port = input("Enter port number: ")
    map_ports.append(map_port)
num_reducers = int(input("Enter your desired number of reduce clusters: "))
reduce_ports = []
for i in range(num_reducers):
    reduce_port = input("Enter port number: ")
    reduce_ports.append(reduce_port)
subprocess.run(args=("py",func,ip_address,str(num_mappers),str(map_ports),str(num_reducers),str(reduce_ports),str(files),output_location,))


