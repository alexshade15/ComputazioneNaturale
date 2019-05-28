import os
from threading import Thread
#import time


class ServerTorcs(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        os.chdir(r'C:\Users\alex\Desktop\torcs')
        #print "SERVER",time.time()
        os.system('wtorcs.exe -t 1000000000 -T >nul 2>nul')

if __name__ == "__main__":
    os.chdir(r'C:\Users\alex\Desktop\torcs')
    os.system('wtorcs.exe -t 1000000000')