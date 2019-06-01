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
        3723.57,  # alpine2
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
            if len(lapT) < 2:
                races[index]['lapTime'] = 300
                races[index]['damage'] = 10000
                races[index]['distance'] = self.track_distances[index]
                races[index]['out'] = [0.0, 0]
            else:
                races[index]['lapTime'] = lapT[1]
                races[index]['damage'] = self.getValuePerLap(dmg)
                races[index]['distance'] = self.getValuePerLap(dist) - self.track_distances[index]
                races[index]['out'] = out

        fit = 0
        for race in races:
            fit += race['lapTime']
            fit += race['damage'] / 2
            fit += race['distance'] * 10
            for elem in race['out']:
                fit += round(elem[1]/25)*3

        print P
        print "lastLapTime--->", races[0]['lapTime'], '--', races[1]['lapTime'], '--', races[2]['lapTime']
        print "damages--->", races[0]['damage'], '--', races[1]['damage'], '--', races[2]['damage']
        print "distance--->", races[0]['distance'], '--', races[1]['distance'], '--', races[2]['distance']
        print "times out--->", len(races[0]['out']), '--', len(races[1]['out']), '--', len(races[2]['out'])
        print "fitness--->", fit

        return [fit]

    def get_bounds(self):
        # y = used_parameters
        y = used_parameters
        LOWER_VECTOR = []
        UPPER_VECTOR = []
        percent = 0.2
        for elem in y:
            if y[elem] > 0:
                UPPER_VECTOR.append(y[elem] + y[elem] * percent)
                LOWER_VECTOR.append(y[elem] - y[elem] * percent)
            if y[elem] < 0:
                UPPER_VECTOR.append(y[elem] - y[elem] * percent)
                LOWER_VECTOR.append(y[elem] + y[elem] * percent)
        return (LOWER_VECTOR, UPPER_VECTOR)


def mySADE(n_trials, n_gen, p_size, new_parameters, n_servers, in_pop=None):
    prob = pg.problem(myProblem())
    print "Problem defined!"
    uda = pg.sade(gen=n_gen, variant=7, variant_adptv=1, memory=False, seed=1234, ftol=1e-6, xtol=1e-6)

    global_results = []
    logs = []
    algo = pg.algorithm(uda)
    results_trial = []

    print "Starting servers"
    servers = []
    for i in range(n_servers):
        servers.append(ServerTorcs.ServerTorcs(port=3001 + i))
        servers[i].start()
        time.sleep(2)
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
    population_size = 10
    n_gens = 1000
    pg.set_global_rng_seed(seed=42)
    new_parameters = "Test01"
    mySADE(n_trials, n_gens, population_size, new_parameters, n_servers)
