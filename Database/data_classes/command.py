from distutils.cmd import Command
from enum import Enum


# The `CommandType` class is an enumeration of the possible command types that can be sent to the server
class CommandType(Enum):
    SET = 0
    GET = 1


# A class that defines the structure of a command.
class Command:
    def getType(self)->CommandType:
        pass
    def getKey(self)->str:
        pass
    def getValue(self)->str:
        pass
    def getTimestamp(self):
        pass
    def attach_pid(self,pid):
        self._pid = pid
    def getPid(self):
        return self._pid


# > A `SetCommand` is a command that sets a key to a value.
class SetCommand(Command):
    def  __init__(self,key,value,timestamp):
        self._key = key
        self._value = value
        self._timestamp = timestamp
        self._pid = 0
    
    def getType(self)->CommandType:
        return CommandType.SET
    def getKey(self)->str:
        return self._key
    def getValue(self)->str:
        return self._value
    def getTimestamp(self):
        return self._timestamp
    
        

# > A `GetCommand` is a command that gets a value using a key.
class GetCommand(Command):
    def  __init__(self,key,timestamp):
        self._key = key
        self._timestamp = timestamp

        self._pid = 0
    
    def getType(self)->CommandType:
        return CommandType.GET
    def getKey(self)->str:
        return self._key
    def getValue(self)->str:
        return None
    def getTimestamp(self):
        return self._timestamp

        



    
