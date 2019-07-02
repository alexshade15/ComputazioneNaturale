import json
import os
import pygmo as pg
import numpy as np
import ServerTorcs
from def_param import new_param
import matplotlib.pyplot as plt
import time
from problems import myProblem, myProblemMultiobj


def mySADE(n_trials, n_gen, p_size, new_parameters, n_servers):

    # uda = pg.sade(gen=n_gen, variant=7, variant_adptv=1, memory=False, seed=1234, ftol=1e-3, xtol=1e-3)
    # pso from pygmo
    udas = []
    udas.append(pg.pso(gen=n_gen, omega=0.7298, eta1=2.05, eta2=2.05, max_vel=0.5, variant=5, neighb_type=2, memory=True,seed=1234))
    udas.append(pg.pso(gen=n_gen, omega=0.7298, eta1=2.05, eta2=2.05, max_vel=0.5, variant=5, neighb_type=4, neighb_param=4, memory=False, seed=1234))

    # pso from slides
    udas.append(pg.pso(gen=n_gen, omega=0.7298, eta1=1.49618, eta2=1.49618, memory=True, seed=1234, max_vel=0.5, variant=5, neighb_type=2))

    udas.append(pg.sade(gen=n_gen, variant=7, variant_adptv=1, memory=False, seed=1234, ftol=1e-3, xtol=1e-3))
    udas.append(pg.sade(gen=n_gen, variant=8, variant_adptv=1, memory=False, seed=1234, ftol=1e-3, xtol=1e-3))
    udas.append(pg.sade(gen=n_gen, variant=18, variant_adptv=1, memory=False, seed=1234, ftol=1e-3, xtol=1e-3))


    # #MULTIOBJ UDAS
    # udas.append(
    #     pg.moead(gen=n_gen, weight_generation="grid", decomposition="tchebycheff", neighbours=20, CR=1, F=.9, eta_m=20))
    # udas.append(
    #     pg.moead(gen=n_gen, weight_generation="low discrepancy", decomposition="tchebycheff", neighbours=20, CR=1,
    #              F=.9, eta_m=20,))
    # udas.append(
    #     pg.moead(gen=n_gen, weight_generation="grid", decomposition="weighted", neighbours=20, CR=1, F=.9, eta_m=20))
    # udas.append(
    #     pg.moead(gen=n_gen, weight_generation="low discrepancy", decomposition="weighted", neighbours=20, CR=1,
    #              F=.9, eta_m=20))

    global_results = []

    print "Starting servers"
    servers = []
    for i in range(n_servers):
        servers.append(ServerTorcs.ServerTorcs(port=3001 + i))
        servers[i].start()
        time.sleep(.5)
    print "Servers started"

    for index, uda in enumerate(udas):
        logs = []
        algo = pg.algorithm(uda)
        results_trial = []

        time.sleep(1)
        print ('uda:', index)

        for i in range(0, n_trials):
            prob1 = pg.problem(myProblem(n_servers, index))
            # prob1 = pg.problem(myProblemMultiobj(n_servers, index))

            log_trial = []
            algo.set_verbosity(1)
            pop = pg.population(prob1, p_size, seed=i+index)
            algo.evolve(pop)
            log_trial.append(algo.extract(type(uda)).get_log())
            log_trial = np.array(log_trial)
            results_trial.append(np.min(log_trial[:, log_trial.shape[1] - 1, 2]))

        logs.append(algo.extract(type(uda)).get_log())
        logs = np.array(logs)
        avg_log = np.average(logs, 0)
        global_results.append(np.min(results_trial, 0))
        plt.plot(avg_log[:, 1], avg_log[:, 2], label=algo.get_name()+str(index))

        P = new_param
        i = 0
        for key in P:
            P[key] = pop.champion_x[i]
            i = i + 1

        with open(new_parameters + str(index) + ".txt", 'w') as outfile:
            json.dump(P, outfile)

        with open("log" + algo.get_name() + '_' + str(time.time()) + '_' + str(index) + ".txt", 'w') as outfile:
            json.dump(algo.extract(type(uda)).get_log(), outfile)

    print("global results: ", global_results)

    P = new_param
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
    population_size = 20
    n_gens = 500
    pg.set_global_rng_seed(seed=27)
    new_parameters = "TestPSO_parameter_by_pygomo"
    mySADE(n_trials, n_gens, population_size, new_parameters, n_servers)
