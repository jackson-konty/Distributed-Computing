from subprocess import Popen, CREATE_NEW_CONSOLE
import sys
Popen(args=("py","client.py",sys.argv[1]),creationflags=CREATE_NEW_CONSOLE)