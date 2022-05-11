import subprocess
import socket
hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname)  
subprocess.run(args=("py","word_count.py",str(IPAddr),str(3),str([1000,1001,1002]),str(3),str([2000,2001,2002]),str(["wp.txt"]),"wc_output1.txt",))
subprocess.run(args=("py","word_count.py",str(IPAddr),str(3),str([1000,1001,1002]),str(3),str([2000,2001,2002]),str(["wp.txt","gg.txt","ks.txt","trca.txt","ts.txt"]),"wc_output2.txt",))
subprocess.run(args=("py","word_count.py",str(IPAddr),str(5),str([1000,1001,1002,1003,1004]),str(5),str([2000,2001,2002,2003,2004]),str(["wp.txt","gg.txt"]),"wc_output3.txt",))
subprocess.run(args=("py","word_count.py",str(IPAddr),str(5),str([1000,1001,1002,1003,1004]),str(5),str([2000,2001,2002,2003,2004]),str(["wp.txt","gg.txt"]),"wc_output4.txt",))