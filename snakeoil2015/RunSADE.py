import Queue
import json
import os
import pygmo as pg
import numpy as np
import ServerTorcs
from def_param import used_parameters, dt7
import matplotlib.pyplot as plt
import time
import client
from threading import Thread


class myProblem:
    counter = 0
    track_distances = [  # 2057.56, # speedway_n1
        3773.57,  # alpine2
        3608.45,  # corkscrew
        5784.10]  # forza

    def getValuePerLap(self, values):
        # valueaPerLap = [values[0]]
        # for i in range(len(values) - 1):
        #     valueaPerLap.append(values[i + 1] - values[i])
        return values[1] - values[0]

    def fitness(self, dv):
        self.counter += 1
        i = 0
        P = used_parameters
        for key in P:
            P[key] = dv[i]
            i = i + 1

        que = Queue.Queue()
        threadsList = list()
        clientCall = lambda P, port, que: que.put(client.main(P, port))

        k = time.time()
        # print "Starting clients"
        for i in range(n_servers):
            threadsList.append(Thread(target=clientCall, args=(P, 3001 + i, que)))
            threadsList[i].start()
        for elem in threadsList:
            elem.join()
        # print "Clients started"
        print '\n\nFitness evaluation', self.counter, 'completed,', 'time:', int(time.time() - k)

        races = [{'lapTime': 0.0, 'damage': 0, 'distance': 0.0, 'out': []},
                 {'lapTime': 0.0, 'damage': 0, 'distance': 0.0, 'out': []},
                 {'lapTime': 0.0, 'damage': 0, 'distance': 0.0, 'out': []}]
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

        print P
        print "lastLapTime--->\t\t", races[0]['lapTime'], '\t\t\t', races[1]['lapTime'], '\t\t\t', races[2]['lapTime']
        print "damages--->\t\t\t", races[0]['damage'], '\t\t\t', races[1]['damage'], '\t\t\t', races[2]['damage']
        print "distance--->\t\t", races[0]['distance'], '\t\t\t', races[1]['distance'], '\t\t\t', races[2]['distance']
        print "times out--->", races[0]['out']
        print "times out--->", races[1]['out']
        print "times out--->", races[2]['out']

        # https://pyformat.info
        # print 'lastLapTime--->{:06.2f}{:06.2f}{:06.2f}'.format(races[0]['lapTime'], races[1]['lapTime'], races[2]['lapTime'])

        fit = 0
        for race in races:
            fit += race['lapTime']
            fit += race['damage'] / 2
            fit += race['distance'] * 3
            try:
                for elem in race['out']:
                    fit += round(elem[1] / 25) * 3
            except:
                print 'ops'

        print "fitness--->", fit

        return [fit]

    def get_bounds(self):
        # y = used_parameters
        # y = used_parameters
        # LOWER_VECTOR = []
        # UPPER_VECTOR = []
        # percent = 0.35
        # for elem in y:
        #     if y[elem] > 0:
        #         UPPER_VECTOR.append(y[elem] + y[elem] * percent)
        #         LOWER_VECTOR.append(y[elem] - y[elem] * percent)
        #     if y[elem] < 0:
        #         UPPER_VECTOR.append(y[elem] - y[elem] * percent)
        #         LOWER_VECTOR.append(y[elem] + y[elem] * percent)
        # return (LOWER_VECTOR, UPPER_VECTOR)
        LOWER_VECTOR = [18.14378789669682, 4561.867327097503, 4864.256208097091, 0.006521516869021103,
                        7744.426773674217,
                        4103.475744152292, 61.94964857622523, 321.36512312089656, 6187.469516868023,
                        0.09349431790669915,
                        58.721654513141935, 0.0008320597508565913, 6192.370654806835, 0.6501724598282282,
                        13.046032260738489,
                        2.916581368987349, 0.06665239745907595, 2608.7773490092113, 0.872603017078228, 46.052905412372,
                        6193.502954634951,
                        32.68917286200262, 0.5329178281232583, 7.171768444030993e-05, 22.01470714149152,
                        1.489708143867886,
                        0.04281359219782884, 0.03342683144585004, 0.6501554789815429, 0.3323749516323206,
                        0.4179008715516361,
                        6274.311660520409, 213.94987796039874, 0.011731068851808843, 10.454125384381236,
                        0.9776444010866587,
                        0.35881318748419, 0.37480085141189734, 7.015813226908676, 0.5560280484705462,
                        0.6749222156487225,
                        -1.2174580673560715, 1.1342413234466129, 448.47103380674605, 1.4576676969620301,
                        1.952880862850981,
                        1.4276892986994985, 0.6176374360205015, 1.0849961114857385, 4829.70181920446]
        UPPER_VECTOR = [37.68325178544725, 9474.6475255102, 10102.685970663188, 0.01354468888181306, 16084.57868378491,
                        8522.603468623991,
                        128.664654735237, 667.4506403280158, 12850.898227341277, 0.19418050642160595,
                        121.96035937344863,
                        0.0017281240979329202, 12861.077513829581, 1.3503581857970892, 27.095605464610703,
                        6.057515150973724,
                        0.13843190241500386, 5418.229878711439, 1.8123293431624732, 95.64834201031105,
                        12863.429213472591,
                        67.89289748262081, 1.106829335332921, 0.00014895211383756675, 45.722853293867,
                        3.094009221879456,
                        0.08892053764164451, 0.06942495761830392, 1.350322917884743, 0.6903172072363581,
                        0.8679479639918595,
                        13031.262679542386, 444.35743884082814, 0.02436452761529529, 21.712414259868723,
                        2.030492217641522,
                        0.7452273893902408, 0.7784325375477866, 14.57130439434879, 1.1548274852849807,
                        1.4017615248088853,
                        -0.5861835139121827, 2.3557319794660416, 931.4398394447802, 3.0274636783057547,
                        4.055983330536653,
                        2.9652008511451116, 1.2827854440425799, 2.253453462316534, 10030.919162963108]
        return (LOWER_VECTOR, UPPER_VECTOR)


def mySADE(n_trials, n_gen, p_size, new_parameters, n_servers, in_pop=None):
    prob = pg.problem(myProblem())
    print "Problem defined!"
    uda = pg.sade(gen=n_gen, variant=18, variant_adptv=1, memory=False, seed=1234, ftol=1e-6, xtol=1e-6)

    global_results = []
    logs = []
    algo = pg.algorithm(uda)
    results_trial = []

    print "Starting servers"
    servers = []
    for i in range(n_servers):
        servers.append(ServerTorcs.ServerTorcs(port=3001 + i))
        servers[i].start()
        time.sleep(.5)
    print "Servers started"

    time.sleep(20)

    for i in range(0, n_trials):
        log_trial = []
        algo.set_verbosity(9)
        if in_pop:
            pop = in_pop
        else:
            pop = pg.population(prob, p_size, seed=1234)
        algo.evolve(pop)
        log_trial.append(algo.extract(type(uda)).get_log())
        log_trial = np.array(log_trial)
        results_trial.append(np.min(log_trial[:, log_trial.shape[1] - 1, 2]))

    logs.append(algo.extract(type(uda)).get_log())
    logs = np.array(logs)
    avg_log = np.average(logs, 0)
    global_results.append(np.min(results_trial, 0))
    plt.plot(avg_log[:, 1], avg_log[:, 2], label=algo.get_name())

    print("global results: ", global_results)

    P = used_parameters
    i = 0
    for key in P:
        P[key] = pop.champion_x[i]
        i = i + 1
    os.chdir(r"C:\Users\alex\Documents\GitHub\ComputazioneNaturale\snakeoil2015")
    print "champion_x", pop.champion_x
    print "champion_f", pop.champion_f
    with open("def_param.py", 'a') as outfile:
        outfile.write(new_parameters + " = " + str(P))
        json.dump(P, outfile)
    with open(new_parameters + ".txt", 'w') as outfile:
        json.dump(P, outfile)
    # We then add details to the plot
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    n_trials = 1
    n_servers = 3
    population_size = 15
    n_gens = 500
    pg.set_global_rng_seed(seed=42)
    new_parameters = "Test01"
    mySADE(n_trials, n_gens, population_size, new_parameters, n_servers)
