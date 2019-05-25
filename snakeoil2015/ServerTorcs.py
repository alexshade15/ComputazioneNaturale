import os
from threading import Thread


class ServerTorcs(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        #print "server running"
        os.chdir(r'C:\Users\alex\Desktop\torcs')
        os.system('wtorcs.exe -t 1000000000 -T >nul 2>nul')
