import json
import os
import pygmo as pg
import numpy as np
import client
import ServerTorcs
from def_param import used_parameters, believe
import matplotlib.pyplot as plt
import time


class myProblem:
    # def getDamagePerLap(self, damages):
    #     damagesPerLap = [damages[0]]
    #     for i in range(len(damages) - 1):
    #         damagesPerLap.append(damages[i + 1] - damages[i])
    #         if sum(damagesPerLap)/3 <= 150:
    #             for i in range(len(damagesPerLap)):
    #                 damagesPerLap[i] = 0
    #     return damagesPerLap

    def fitness(self, dv):
        i = 0
        P = used_parameters
        for key in P:
            P[key] = dv[i]
            i = i + 1

        server1 = ServerTorcs.ServerTorcs()
        server1.start()
        (lapTimes, damages) = client.main(P, 3001)

        print "\n", P

        if len(lapTimes)<2:
            FAIL = '\033[91m'
            print FAIL + "Timeout" + FAIL
            return [10000]

        print "lastLapTime--->", lapTimes[1]


        damagePerLap = damages[1] - damages[0] #self.getDamagePerLap(damages)
        print "damages--->", damagePerLap
        # fitness1 = [lap + dmg / 2 for lap, dmg in zip(lapTimes, damagePerLap)]
        # fitness_mean_tot = sum(fitness1) / float(len(fitness1))

        fitness1 = lapTimes[1] + damagePerLap / 2
        print "fitness--->", fitness1#, "----- mean: ", fitness_mean_tot, "\n"
        #return [fitness_mean_tot]
        return [fitness1]

    def get_bounds(self):
        y = used_parameters
        LOWER_VECTOR = []
        UPPER_VECTOR = []
        percent = 0.1
        for elem in y:
            if y[elem] > 0:
                UPPER_VECTOR.append(y[elem] + y[elem] * percent)
                LOWER_VECTOR.append(y[elem] - y[elem] * percent)
            if y[elem] < 0:
                UPPER_VECTOR.append(y[elem] - y[elem] * percent)
                LOWER_VECTOR.append(y[elem] + y[elem] * percent)
            if y[elem] == 0:
                UPPER_VECTOR.append(10)
                LOWER_VECTOR.append(-10)
        return (LOWER_VECTOR, UPPER_VECTOR)


def mySADE(n_trials, n_gen, p_size, new_parameters, in_pop=None):
    prob = pg.problem(myProblem())
    print "Problem defined!"
    uda = pg.sade(gen=n_gen, variant=2, variant_adptv=1, memory=False, seed=1234, ftol=1e-20, xtol=1e-20)
    global_results = []
    logs = []
    algo = pg.algorithm(uda)
    results_trial = []
    for i in range(0, n_trials):
        log_trial = []
        algo.set_verbosity(9)
        if in_pop:
            pop = in_pop
        else:
            pop = pg.population(prob, p_size)
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
    population_size = 10
    n_gens = 100
    pg.set_global_rng_seed(seed=42)
    new_parameters = "Test28_after_prooning"
    mySADE(n_trials, n_gens, population_size, new_parameters)
