class ProcessInfo:
    def __init__(self,process_id, ip, port_number):
        self.process_id = process_id
        self.port_number = port_number
        #self.vector_clock = vector_clock
        self.ip = ip

    #Returns full port for this process
    def getPort(self):
        return f"tcp://{self.ip}:{self.port_number}"

class ServerInfo:
    def __init__(self,process_id, ip, client_port_number,server_port_number):
        self.process_id = process_id
        self.ip = ip
        self.client_port_number = client_port_number
        self.server_port_number = server_port_number
    def getClientPort(self):
        return f"tcp://{self.ip}:{self.client_port_number}"
    def getServerPort(self):
        return f"tcp://{self.ip}:{self.server_port_number}"

    