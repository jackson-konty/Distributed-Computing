def cleanMessage(command_string):
    """
    It takes a string, splits it into a list, and returns a list of the command and the key and value if
    it's a valid set command, or just the key if it's a valid get command
    
    :param command_string: The string that the user has entered
    :return: A list of strings.
    """
    command_string = command_string.strip()
    command_list = command_string.split()
    if(len(command_list)<=1):
        return []
    elif(len(command_list)==2 and isGet(command_list[0])):
        command_list[1] = command_list[1]
        return command_list
    elif(isSet(command_list[0]) and isValidKey(command_list[1]) and len(command_list) >= 3):
        val_str = ""
        for word in command_list[2:]:
            val_str += word+" " 
        return [command_list[0],command_list[1],val_str]
    return []  


def isSet(command_type : str)->bool:
    """
    > This function takes a string and returns a boolean indicating whether the string is equal to "set"

    :param command_type: The command type, which is either "get" or "set"
    :type command_type: str
    :return: A boolean value
    """
    command_type = command_type.lower()
    return command_type == "set"



def isGet(command_type : str)->bool:
    """
    This function takes a string and returns a boolean indicating whether or not the string is equal to
    the word 'get' in lowercase.
    
    :param command_type: The type of command that the user is trying to execute
    :type command_type: str
    :return: A boolean value
    """
    command_type = command_type.lower()
    return command_type == "get"



def isValidKey(key : str)->bool:
    """
    It returns True if the key is alphanumeric, and False otherwise
    
    :param key: The key to be used for encryption/decryption
    :type key: str
    :return: True or False
    """
    return key.isalnum()