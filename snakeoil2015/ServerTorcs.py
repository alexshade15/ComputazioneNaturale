import os
from threading import Thread

class ServerTorcs(Thread):

    def __init__(self, port=3001):
        Thread.__init__(self)
        self.port = port

    def run(self):
        os.chdir('C:\\Users\\alex\\Desktop\\torcs' + str(self.port))
        #print "SERVER",time.time()
        os.system('wtorcs.exe -t 1000000000 -T >NUL')


if __name__ == "__main__":
    os.chdir(r'C:\Users\alex\Desktop\torcs3004')
    os.system('wtorcs.exe -t 1000000000')