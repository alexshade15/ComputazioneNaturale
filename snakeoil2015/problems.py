import client
import Queue
import time
from threading import Thread
from def_param import used_parameters_V3


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

    def __init__(self, n_servers, index):
        self.n_servers = n_servers
        self.index = index

    def getValuePerLap(self, values):
        # valueaPerLap = [values[0]]
        # for i in range(len(values) - 1):
        #     valueaPerLap.append(values[i + 1] - values[i])
        return values[1] - values[0]

    def fitness(self, dv):
        self.counter += 1
        i = 0
        P = used_parameters_V3

        for key in P:
            P[key] = dv[i]
            i = i + 1

        que = Queue.Queue()
        threadsList = list()
        clientCall = lambda P, port, que: que.put(client.main(P, port))

        k = time.time()
        # print "Starting clients"
        for i in range(self.n_servers):
            threadsList.append(Thread(target=clientCall, args=(P, 3001 + i, que)))
            threadsList[i].start()
        for elem in threadsList:
            elem.join()
        # print "Clients started"
        print '\n\nFitness evaluation', self.counter, 'completed,', 'time:', int(time.time() - k), '--',self.index

        races = [
            {'lapTime': 0.0, 'damage': 0, 'distance': 0.0, 'out': []},
            # {'lapTime': 0.0, 'damage': 0, 'distance': 0.0, 'out': []}#,
            # {'lapTime': 0.0, 'damage': 0, 'distance': 0.0, 'out': []}
        ]

        try:
            while que.qsize() > 0:
                (lapT, dmg, dist, out, p) = que.get()
                index = p % 3001
                # print "--lapT, dmg, dist-->", lapT, dmg, dist
                if len(dmg) < 2 or dmg[len(dmg) - 1] > 10000:
                    races[index]['lapTime'] = 300
                    races[index]['damage'] = 10000
                    races[index]['distance'] = self.track_distances[index]
                else:
                    races[index]['lapTime'] = lapT[1]
                    races[index]['damage'] = self.getValuePerLap(dmg)
                    races[index]['distance'] = self.getValuePerLap(dist) - self.track_distances[index]
                    races[index]['out'] = out
        except:
            print 'grrr'

        print P
        print "lastLapTime---> ", races[0][
            'lapTime']  # , ' -- ', races[1]['lapTime']#, ' -- '#, races[2]['lapTime']#, ' -- ', races[3]['lapTime']
        print "damages---> ", races[0][
            'damage']  # , ' -- ', races[1]['damage']#, ' -- '#, races[2]['damage']#, ' -- ', races[3]['damage']
        print "distance---> ", races[0][
            'distance']  # , ' --- ', races[1]['distance'], ' --- ', races[2]['distance'], ' --- ', races[3]['distance']
        print "times out--->", races[0]['out']
        # print "times out--->", races[1]['out']
        # print "times out--->", races[2]['out']
        # print "times out--->", races[3]['out']
        print 'damage:', dv[35], 'distance', dv[25], 'out', dv[8]

        # https://pyformat.info
        # print 'lastLapTime--->{:06.2f}{:06.2f}{:06.2f}'.format(races[0]['lapTime'], races[1]['lapTime'], races[2]['lapTime'])

        fit = 0
        for race in races:
            fit += race['lapTime']
            fit += race['damage'] / dv[35]
            # fit += race['distance'] * dv[25]
            try:
                for elem in race['out']:
                    fit += round(elem[1] * dv[8])
            except:
                print 'ops'

        print "fitness--->", fit

        return [fit]

    def get_bounds(self):
        # y = used_parameters_V3
        # LOWER_VECTOR = []
        # UPPER_VECTOR = []
        # percent = 0.2
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
        #
        #
        # # LOWER_VECTOR = [22.330815872857627, 5614.605941043081, 5986.776871504111, 0.008026482300333666, 7500,
        # #                 5050.431685110512, 76.24572132458489, 395.5263053795649, 7500, 0.11506992973132205,
        # #                 72.27280555463622, 0.0010240735395158046, 7500, 0.800212258250127, 16.056655090139678,
        # #                 3.589638607984429, 0.08203371994963192, 3210.80289108826, 1.0739729440962804, 56.68049896907322,
        # #                 7500, 40.232828137849374, 0.6558988653824718, 8.826791931115067e-05, 27.095024174143408,
        # #                 1.8334869462989367, 0.05269365193578934, 0.041140715625661586, 0.8001913587465144,
        # #                 0.4090768635474715, 0.5143395342173982, 7500, 263.3229267204907, 0.014438238586841654,
        # #                 12.866615857699983, 1.2032546474912722, 0.4416162307497723, 0.4612933555838736,
        # #                 8.634847048502987, 0.6843422135022108, 0.8306734961830431, -1.0821849487609525,
        # #                 1.3959893211650618, 551.9643493006105, 1.7940525501071138, 2.4035456773550536,
        # #                 1.757156059937844, 0.7601691520252325, 1.335379829520909, 5944.248392867027]
        # # UPPER_VECTOR = [33.49622380928644, 8421.908911564622, 8980.165307256168, 0.012039723450500497, 9000,
        # #                 7575.647527665769, 114.36858198687735, 593.2894580693473, 9000, 0.17260489459698306,
        # #                 108.40920833195435, 0.001536110309273707, 9000, 1.2003183873751906, 24.084982635209514,
        # #                 5.384457911976644, 0.12305057992444789, 4816.204336632391, 1.6109594161444207,
        # #                 85.02074845360983, 9000, 60.34924220677406, 0.9838482980737076, 0.00013240187896672602,
        # #                 40.64253626121511, 2.750230419448405, 0.07904047790368401, 0.06171107343849237,
        # #                 1.2002870381197714, 0.6136152953212073, 0.7715093013260974, 9000, 394.98439008073615,
        # #                 0.02165735788026248, 19.299923786549975, 1.8048819712369084, 0.6624243461246585,
        # #                 0.6919400333758103, 12.952270572754479, 1.026513320253316, 1.2460102442745646,
        # #                 -0.7214566325073017, 2.0939839817475927, 827.9465239509158, 2.691078825160671,
        # #                 3.6053185160325802, 2.635734089906766, 1.1402537280378489, 2.003069744281363, 8916.372589300541]

        LOWER_VECTOR = [8.374055952321612, 3500, 3500, 0.003009930862625125, 7000, 3500, 28.59214549671934,
                        148.3223645173369, 0.000000001, 7000, 0.04315122364924577, 27.102302082988587,
                        0.0003840275773184268,
                        0.030762644981111975, 0.3000795968437977, 0.6589335224766917, 6.02124565880238,
                        1.3461144779941612, 7000, 3500, 0.40273985403610524, 21.255187113402464, 7000, 0.000000001,
                        15.08731055169352, 0.2459620745184269, 10.160634065303778, 4.824980946637494, 4.824980946637494,
                        0.005414339470065621, 0.3000717595299429, 0.15340382383030182, 0.19287732533152435, 7000,
                        98.74609752018404, 0.000000001, 0.015427768359623097, 0.6875576048621013, 0.16560608653116465,
                        0.17298500834395264, 0.37317478133882886, 0.2566283300633291, 0.31150256106864116,
                        0.5234959954368983, 206.98663098772897, 0.6727697062901679, 0.9013296290081452,
                        0.45122049280922716, 0.28506343200946227, 0.5007674360703409, 3500]
        UPPER_VECTOR = [47.452983729822456, 6000, 6000, 0.017056274888209037, 9500, 6000, 162.0221578147429,
                        840.4933989315755, 1, 9500, 0.24452360067905932, 153.57971180360198, 0.0021761562714710846,
                        0.17432165489296783, 1.7004510487815199, 3.7339566273679186, 34.12039206654681,
                        7.627982041966911, 9500, 6000, 2.282192506204596, 120.4460603092806, 9500, 1, 85.49475979292991,
                        1.3937850889377525, 57.576926370054736, 27.341558697612463, 27.341558697612463,
                        0.03068125699703851, 1.700406637336343, 0.869288335038377, 1.0929715102119713, 9500,
                        559.5612192810429, 10, 0.08742402070453087, 3.8961597608852405, 0.9384344903432662,
                        0.9802483806157314, 2.1146570942533636, 1.4542272036921977, 1.7651811793889665,
                        2.966477307475756, 1172.9242422637972, 3.812361668977617, 5.107534564379488, 2.5569161259189537,
                        1.615359448053619, 2.8376821377319312, 6000]

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
        return 4

    def fitness(self, dv):
        self.counter += 1
        i = 0
        P = used_parameters_V3

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
        print "distance---> ", races[0][
            'distance']  # , ' --- ', races[1]['distance'], ' --- ', races[2]['distance'], ' --- ', races[3]['distance']
        print "times out--->", races[0]['out']
        # print "times out--->", races[1]['out']
        # print "times out--->", races[2]['out']
        # print "times out--->", races[3]['out']
        print 'damage:', dv[35], 'distance', dv[25], 'out', dv[8]

        fit = []
        for race in races:
            fit.append(race['lapTime'])
            fit.append(race['damage'] / dv[35])
            fit.append(race['distance'] * dv[25])
            try:
                tmp = 0
                for elem in race['out']:
                    tmp += round(elem[1] * dv[8])
                fit.append(tmp)
            except:
                print 'ops'

        print "fitness--->", fit

        return fit

    def  get_bounds(self):
        LOWER_VECTOR = [8.374055952321612, 3500, 3500, 0.003009930862625125, 7000, 3500, 28.59214549671934,
                        148.3223645173369, 0.000000001, 7000, 0.04315122364924577, 27.102302082988587,
                        0.0003840275773184268,
                        0.030762644981111975, 0.3000795968437977, 0.6589335224766917, 6.02124565880238,
                        1.3461144779941612, 7000, 3500, 0.40273985403610524, 21.255187113402464, 7000, 0.000000001,
                        15.08731055169352, 0.2459620745184269, 10.160634065303778, 4.824980946637494, 4.824980946637494,
                        0.005414339470065621, 0.3000717595299429, 0.15340382383030182, 0.19287732533152435, 7000,
                        98.74609752018404, 0.000000001, 0.015427768359623097, 0.6875576048621013, 0.16560608653116465,
                        0.17298500834395264, 0.37317478133882886, 0.2566283300633291, 0.31150256106864116,
                        0.5234959954368983, 206.98663098772897, 0.6727697062901679, 0.9013296290081452,
                        0.45122049280922716, 0.28506343200946227, 0.5007674360703409, 3500]
        UPPER_VECTOR = [47.452983729822456, 6000, 6000, 0.017056274888209037, 9500, 6000, 162.0221578147429,
                        840.4933989315755, 1, 9500, 0.24452360067905932, 153.57971180360198, 0.0021761562714710846,
                        0.17432165489296783, 1.7004510487815199, 3.7339566273679186, 34.12039206654681,
                        7.627982041966911, 9500, 6000, 2.282192506204596, 120.4460603092806, 9500, 1, 85.49475979292991,
                        1.3937850889377525, 57.576926370054736, 27.341558697612463, 27.341558697612463,
                        0.03068125699703851, 1.700406637336343, 0.869288335038377, 1.0929715102119713, 9500,
                        559.5612192810429, 10, 0.08742402070453087, 3.8961597608852405, 0.9384344903432662,
                        0.9802483806157314, 2.1146570942533636, 1.4542272036921977, 1.7651811793889665,
                        2.966477307475756, 1172.9242422637972, 3.812361668977617, 5.107534564379488, 2.5569161259189537,
                        1.615359448053619, 2.8376821377319312, 6000]
        return (LOWER_VECTOR, UPPER_VECTOR)
