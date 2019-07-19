import json
import os

import client
import Queue
import time
from threading import Thread
import def_param
from def_param import new_param

from dictionaries import UPPER, LOWER


class myProblem:
    counter = 0
    track_distances = [
        2057.56,  # speedway_n1
        3274.20,
        # 3773.57,  # alpine2
        4203.37,  # E-track
        # 3823.05,  # CG track3
        5784.10,  # forza
        3608.45,  # corkscrew
    ]

    def __init__(self, n_servers, index, par_name, n_gen, p_size, today, algo_name, new_parameters, offset):
        self.n_servers = n_servers
        self.index = index
        self.par_name = par_name
        self.n_gen = n_gen
        self.p_size = p_size
        self.today = today
        self.algo_name = algo_name
        self.new_parameters = new_parameters
        self.offset = offset

    def getValuePerLap(self, values):
        valueaPerLap = [values[0]]
        for i in range(len(values) - 1):
            valueaPerLap.append(values[i + 1] - values[i])
        return valueaPerLap
        # return values[1] - values[0]

    def fitness(self, dv):
        self.counter += 1

        P = def_param.used_parameters
        # print "new", new_param
        for i, key in enumerate(P):
            P[key] = dv[i]
        # print "P", P

        que = Queue.Queue()
        threadsList = list()
        clientCall = lambda P, port, que: que.put(client.main(P, port))

        k = time.time()
        # print "Starting clients"
        for i in range(self.n_servers):
            threadsList.append(Thread(target=clientCall, args=(P, 3001 + i + self.offset, que)))
            threadsList[i].start()
        for elem in threadsList:
            elem.join()
        # print "Clients started"
        print '\n\nFitness evaluation', self.counter, 'completed,', 'time:', int(time.time() - k), '--', self.index

        races = [
            {'lapTime': [], 'damage': [], 'distance': 0.0, 'out': []},
            {'lapTime': 0.0, 'damage': 0, 'distance': 0.0, 'out': []},
            {'lapTime': 0.0, 'damage': 0, 'distance': 0.0, 'out': []}
        ]

        try:
            while que.qsize() > 0:
                (lapT, dmg, dist, out, p) = que.get()
                index = p % (3001 + self.offset)
                # print "--lapT, dmg, dist-->", lapT, dmg, dist
                if len(dmg) < 2 or dmg[len(dmg) - 1] > 10000:
                    races[index]['lapTime'] = [300]
                    races[index]['damage'] = [10000]
                    # races[index]['distance'] = self.track_distances[index]
                else:
                    races[index]['lapTime'] = lapT[2:]
                    races[index]['damage'] = self.getValuePerLap(dmg)
                    # races[index]['distance'] = self.getValuePerLap(dist) - self.track_distances[index]
                    races[index]['out'] = out
        except:
            print 'exception, queue size:', que.qsize()

        print P
        print "lastLapTime---> ", races[0][
            'lapTime'], ' -- ', races[1]['lapTime'], ' -- ', races[2]['lapTime']  # , ' -- ', races[3]['lapTime']
        print "damages---> ", races[0][
            'damage'], ' -- ', races[1]['damage'], ' -- ', races[2]['damage']  # , ' -- ', races[3]['damage']
        # print "distance---> ", races[0][
        #     'distance']# , ' --- ', races[1]['distance'], ' --- ', races[2]['distance'], ' --- ', races[3]['distance']
        print "times out--->", races[0]['out']
        print "times out--->", races[1]['out']
        print "times out--->", races[2]['out']
        # print "times out--->", races[3]['out']
        # print 'damage:', dv[33], 'out', dv[8]

        fit = 0
        for race in races:
            try:
                fit += sum(race['lapTime']) / len(race['lapTime'])
            except:
                print race['lapTime'], sum(race['lapTime']), len(race['lapTime'])
            try:
                fit += sum(race['damage']) / len(race['damage']) / 3
            except:
                print "Division by zero", sum(race['damage']), len(race['damage'])
            # fit += race['distance'] * dv[25]
            try:
                for elem in race['out']:
                    fit += round(elem[1] * 3 / 25 * elem[0])
            except:
                print 'ops'

        print "fitness--->", fit

        os.chdir(r"C:\Users\Vincenzo\Documents\GitHub\ComputazioneNaturale\snakeoil2015")

        filename = self.new_parameters + "_LOG_" + self.par_name + "_nGen" + str(self.n_gen) + "_pSize" + str(
            self.p_size) + "_circ" + str(self.n_servers) + "_" + self.algo_name + str(index) + "_today" + str(
            self.today)
        with open(filename + ".txt", 'a') as outfile:
            temp_log = {"algo": self.index, "gen": self.counter, "fitness": fit, "races": races, "param": P}
            outfile.write("evaluation_" + str(self.index) + "_" + str(self.counter) + " = " + str(temp_log) + "\n")

        return [fit]

    def get_bounds(self):

        # y = new_param
        # LOWER_VECTOR = []
        # UPPER_VECTOR = []
        # percent = 0.7
        # for elem in y:
        #     if y[elem] > 0:
        #         if elem.find("damage") >= 0:
        #             UPPER_VECTOR.append(10)
        #             LOWER_VECTOR.append(0.0001)
        #         elif elem.find("timesout") >= 0:
        #             UPPER_VECTOR.append(1)
        #             LOWER_VECTOR.append(0.0001)
        #         else:
        #             UPPER_VECTOR.append(y[elem] + y[elem] * percent)
        #             LOWER_VECTOR.append(y[elem] - y[elem] * percent)

        # y = new_param
        # LOWER_VECTOR = []
        # UPPER_VECTOR = []
        # percent = 0.7
        # for elem in y:
        #     if y[elem] > 0:
        #         if elem.find("upsh") >= 0:
        #             UPPER_VECTOR.append(9500)
        #             LOWER_VECTOR.append(7000)
        #         elif elem.find("dnsh") >= 0:
        #             UPPER_VECTOR.append(6000)
        #             LOWER_VECTOR.append(3500)
        #         elif elem.find("damage") >= 0:
        #             UPPER_VECTOR.append(10)
        #             LOWER_VECTOR.append(0)
        #         elif elem.find("distance") >= 0:
        #             UPPER_VECTOR.append(1)
        #             LOWER_VECTOR.append(0)
        #         elif elem.find("timesout") >= 0:
        #             UPPER_VECTOR.append(1)
        #             LOWER_VECTOR.append(0)
        #         else:
        #             UPPER_VECTOR.append(y[elem] + y[elem] * percent)
        #             LOWER_VECTOR.append(y[elem] - y[elem] * percent)
        #     if y[elem] < 0:
        #         UPPER_VECTOR.append(y[elem] - y[elem] * percent)
        #         LOWER_VECTOR.append(y[elem] + y[elem] * percent)
        #     if y[elem] == 0:
        #         print elem

        UPPER_VECTOR = [47.452983729822456, 6000, 6000, 0.017056274888209037, 9500, 6000, 162.0221578147429, 840.4933989315755, 9500, 0.24452360067905932, 153.57971180360198, 0.0021761562714710846, 9500, 1.7004510487815199, 34.12039206654681, 7.627982041966911, 0.17432165489296783, 6000, 2.282192506204596, 120.4460603092806, 9500, 85.49475979292991, 1.3937850889377525, 0.00018756932853619516, 57.576926370054736, 3.8961597608852405, 0.11197401036355235, 0.08742402070453087, 1.700406637336343, 0.869288335038377, 1.0929715102119713, 9500, 559.5612192810429, 0.03068125699703851, 27.341558697612463, 2.5569161259189537, 0.9384344903432662, 0.9802483806157314, 18.349049978068845, 1.4542272036921977, 1.7651811793889665, -0.2927063008345987, 2.966477307475756, 1172.9242422637972, 3.812361668977617, 5.107534564379488, 3.7339566273679186, 1.615359448053619, 2.8376821377319312, 6000]
        LOWER_VECTOR = [8.374055952321612, 3500, 3500, 0.003009930862625125, 7000, 3500, 28.59214549671934, 148.3223645173369, 7000, 0.04315122364924577, 27.102302082988587, 0.0003840275773184268, 7000, 0.3000795968437977, 6.02124565880238, 1.3461144779941612, 0.030762644981111975, 3500, 0.40273985403610524, 21.255187113402464, 7000, 15.08731055169352, 0.2459620745184269, 3.310046974168151e-05, 10.160634065303778, 0.6875576048621013, 0.019760119475921004, 0.015427768359623097, 0.3000717595299429, 0.15340382383030182, 0.19287732533152435, 7000, 98.74609752018404, 0.005414339470065621, 4.824980946637494, 0.45122049280922716, 0.16560608653116465, 0.17298500834395264, 3.2380676431886206, 0.2566283300633291, 0.31150256106864116, -1.6586690380627254, 0.5234959954368983, 206.98663098772897, 0.6727697062901679, 0.9013296290081452, 0.6589335224766917, 0.28506343200946227, 0.5007674360703409, 3500]

        return (LOWER_VECTOR, UPPER_VECTOR)


class myProblemMultiobj:
    counter = 0
    track_distances = [
        2057.56,  # speedway_n1
        3274.20,
        # 3773.57,  # alpine2
        4203.37,  # E-track
        # 3823.05,  # CG track3
        5784.10,  # forza
        3608.45,  # corkscrew
    ]

    def __init__(self, n_servers, index):
        self.n_servers = n_servers
        self.index = index

    def getValuePerLap(self, values):
        return values[1] - values[0]

    def get_nobj(self):
        return 3

    def fitness(self, dv):
        self.counter += 1
        i = 0
        P = new_param

        for key in P:
            P[key] = dv[i]
            i = i + 1

        que = Queue.Queue()
        threadsList = list()
        clientCall = lambda P, port, que: que.put(client.main(P, port))

        k = time.time()
        for i in range(self.n_servers):
            threadsList.append(Thread(target=clientCall, args=(P, 3001 + i, que)))
            threadsList[i].start()
        for elem in threadsList:
            elem.join()
        print '\n\nFitness evaluation', self.counter, 'completed,', 'time:', int(time.time() - k), '---', self.index

        races = [
            {'lapTime': 0.0, 'damage': 0, 'distance': 0.0, 'out': []},
            # {'lapTime': 0.0, 'damage': 0, 'distance': 0.0, 'out': []}#,
            # {'lapTime': 0.0, 'damage': 0, 'distance': 0.0, 'out': []}
        ]
        while que.qsize() > 0:
            (lapT, dmg, dist, out, p) = que.get()
            index = p % 3001
            if len(dmg) < 2 or dmg[len(dmg) - 1] > 10000:
                races[index]['lapTime'] = 300
                races[index]['damage'] = 10000
                races[index]['distance'] = self.track_distances[index]
            else:
                races[index]['lapTime'] = lapT[1]
                races[index]['damage'] = self.getValuePerLap(dmg)
                races[index]['distance'] = self.getValuePerLap(dist) - self.track_distances[index]
                races[index]['out'] = out

        print P
        print "lastLapTime---> ", races[0][
            'lapTime']  # , ' -- ', races[1]['lapTime']#, ' -- '#, races[2]['lapTime']#, ' -- ', races[3]['lapTime']
        print "damages---> ", races[0][
            'damage']  # , ' -- ', races[1]['damage']#, ' -- '#, races[2]['damage']#, ' -- ', races[3]['damage']
        # print "distance---> ", races[0][
        #     'distance']  # , ' --- ', races[1]['distance'], ' --- ', races[2]['distance'], ' --- ', races[3]['distance']
        print "times out--->", races[0]['out']
        # print "times out--->", races[1]['out']
        # print "times out--->", races[2]['out']
        # print "times out--->", races[3]['out']
        print 'damage:', dv[28], 'out', dv[29]

        fit = []
        for race in races:
            fit.append(race['lapTime'])
            fit.append(race['damage'] / dv[28])
            # fit.append(race['distance'] * dv[25])
            try:
                tmp = 0
                for elem in race['out']:
                    tmp += round(elem[1] * dv[29])
                fit.append(tmp)
            except:
                print 'ops'

        print "fitness--->", fit

        return fit

    def get_bounds(self):
        LOWER_VECTOR = [8.374055952321612, 2105.477227891156, 2245.041326814042, 0.003009930862625125, 3574.35081861887,
                        1893.9118819164423, 28.59214549671934, 148.3223645173369, 2855.755161631395,
                        0.04315122364924577, 27.102302082988587, 0.0003840275773184268, 2858.0172252954626,
                        0.3000795968437977, 6.02124565880238, 1.3461144779941612, 0.030762644981111975,
                        1204.0510841580976, 0.40273985403610524, 21.255187113402464, 2858.5398252161312,
                        15.08731055169352, 0.2459620745184269, 3.310046974168151e-05, 10.160634065303778,
                        0.6875576048621013, 0.019760119475921004, 0.015427768359623097, 0.3000717595299429,
                        0.15340382383030182, 0.19287732533152435, 2895.836151009419, 98.74609752018404,
                        0.005414339470065621, 4.824980946637494, 0.45122049280922716, 0.16560608653116465,
                        0.17298500834395264, 3.2380676431886206, 0.2566283300633291, 0.31150256106864116,
                        0.5234959954368983, 206.98663098772897, 0.6727697062901679, 0.9013296290081452,
                        0.6589335224766917, 0.28506343200946227, 0.5007674360703409, 2229.0931473251358]
        UPPER_VECTOR = [8.374055952321612, 2105.477227891156, 2245.041326814042, 0.003009930862625125, 3574.35081861887,
                        1893.9118819164423, 28.59214549671934, 148.3223645173369, 2855.755161631395,
                        0.04315122364924577, 27.102302082988587, 0.0003840275773184268, 2858.0172252954626,
                        0.3000795968437977, 6.02124565880238, 1.3461144779941612, 0.030762644981111975,
                        1204.0510841580976, 0.40273985403610524, 21.255187113402464, 2858.5398252161312,
                        15.08731055169352, 0.2459620745184269, 3.310046974168151e-05, 10.160634065303778,
                        0.6875576048621013, 0.019760119475921004, 0.015427768359623097, 0.3000717595299429,
                        0.15340382383030182, 0.19287732533152435, 2895.836151009419, 98.74609752018404,
                        0.005414339470065621, 4.824980946637494, 0.45122049280922716, 0.16560608653116465,
                        0.17298500834395264, 3.2380676431886206, 0.2566283300633291, 0.31150256106864116,
                        0.5234959954368983, 206.98663098772897, 0.6727697062901679, 0.9013296290081452,
                        0.6589335224766917, 0.28506343200946227, 0.5007674360703409, 2229.0931473251358]
        return (LOWER_VECTOR, UPPER_VECTOR)
