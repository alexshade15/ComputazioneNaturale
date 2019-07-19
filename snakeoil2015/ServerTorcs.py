import os
from threading import Thread

class ServerTorcs(Thread):

    def __init__(self, port=3001):
        Thread.__init__(self)
        self.port = port

    def run(self):
        os.chdir('C:\\Users\\Vincenzo\\Desktop\\torcs' + str(self.port))
        #print "SERVER",time.time()
        os.system('wtorcs.exe -t 1000000000 >NUL')


if __name__ == "__main__":
    os.chdir(r'C:\Users\Vincenzo\Desktop\torcs3005')
    os.system('wtorcs.exe -t 1000000000')