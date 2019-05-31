import os
from threading import Thread
#import time


class ServerTorcs(Thread):
    port = ""

    def __init__(self, port = ""):
        Thread.__init__(self)
        self.port = port

    def run(self):
        os.chdir('C:\\Users\\alex\\Desktop\\torcs' + self.port)
        #print "SERVER",time.time()
        os.system('wtorcs.exe -t 1000000000 -T >NUL')

if __name__ == "__main__":
    os.chdir(r'C:\Users\alex\Desktop\torcs3')
    os.system('wtorcs.exe -t 1000000000')