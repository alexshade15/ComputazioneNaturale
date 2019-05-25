import pygmo as pg
import numpy as np
import client
from ServerTorcs import ServerTorcs
from def_param import default_parameters
import matplotlib.pyplot as plt

class myProblem:
    def fitness(self, dv):
        #print "fitenss called"

        i = 0
        P = default_parameters
        for key in P:
            P[key] = dv[i]
            i = i + 1

        server = ServerTorcs()
        server.start()
        (lastLapTime, damages) = client.main(P)

        print "lastLapTime--->",lastLapTime
        print "damages--->", damages

        return [lastLapTime[2] + damages[2] / 10]

    def get_bounds(self):
        #print "get_bounds called"
        y = default_parameters

        LOWER_VECTOR = []
        UPPER_VECTOR = []
        for elem in y:
            if y[elem] > 0:
                UPPER_VECTOR.append(y[elem] + y[elem] * 10 / 100)
                LOWER_VECTOR.append(y[elem] - y[elem] * 10 / 100)
            if y[elem] < 0:
                UPPER_VECTOR.append(y[elem] - y[elem] * 10 / 100)
                LOWER_VECTOR.append(y[elem] + y[elem] * 10 / 100)
            if y[elem] == 0:
                UPPER_VECTOR.append(5)
                LOWER_VECTOR.append(-5)
        return (LOWER_VECTOR, UPPER_VECTOR)



if __name__ == "__main__":
    n_gens = 10

    pg.set_global_rng_seed(seed=32)

    print 'Problem defined'
    prob = pg.problem(myProblem())

    n_trials = 20
    pop_size = 20
    n_gens = 100

    uda = pg.sade(gen=n_gens, variant=18, variant_adptv=1, memory=False, seed=1234)

    global_results = []
    logs = []
    algo = pg.algorithm(uda)
    results_trial = []
    for i in range(0, n_trials):
        log_trial = []
        # regulates both screen and log verbosity
        algo.set_verbosity(9)
        pop = pg.population(prob, pop_size)
        algo.evolve(pop)
        log_trial.append(algo.extract(type(uda)).get_log())
        log_trial = np.array(log_trial)
        results_trial.append(np.min(log_trial[:, log_trial.shape[1] - 1, 2]))
    logs.append(algo.extract(type(uda)).get_log())
    logs = np.array(logs)
    avg_log = np.average(logs, 0)
    global_results.append(np.min(results_trial, 0))
    plt.plot(avg_log[:, 1], avg_log[:, 2], label=algo.get_name())

    print(global_results)

    # We then add details to the plot
    plt.legend()
    plt.grid()
    plt.show()


    # algo = pg.algorithm(pg.sade(gen=n_gens, variant=18, variant_adptv=1, memory=False, seed=1234, ftol=1e-20, xtol=1e-20))
    # algo.set_verbosity(9)
    # # 3 - Instantiate an archipelago with 16 islands having each 20 individuals
    # archi = pg.archipelago(16, algo=algo, prob=prob, pop_size=20)
    #
    # # 4 - Run the evolution in parallel on the 16 separate islands 10 times.
    # archi.evolve(10)
    #
    # # 5 - Wait for the evolutions to be finished
    # archi.wait()
    #
    # # 6 - Print the fitness of the best solution in each island
    # res = [isl.get_population().champion_f for isl in archi]
    # print(res)