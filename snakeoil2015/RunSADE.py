import datetime
import json
import os
import pygmo as pg
import numpy as np
import ServerTorcs
from def_param import new_param, used_parameters, used_parameters_V1, used_parameters_V2, used_parameters_V3, \
    used_parameters_V4, used_parameters_V5, used_parameters_V6
import matplotlib.pyplot as plt
import time
from problems import myProblem, myProblemMultiobj


def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]


def mySADE(n_trials, n_gen, p_size, new_parameters, n_servers, offset):
    # uda = pg.sade(gen=n_gen, variant=7, variant_adptv=1, memory=False, seed=1234, ftol=1e-3, xtol=1e-3)
    # pso from pygmo
    udas = []
    udas.append(
        pg.pso(gen=n_gen, omega=0.7298, eta1=2.05, eta2=2.05, max_vel=0.5, variant=5, neighb_type=2, memory=True,
               seed=1234))
    # udas.append(pg.pso(gen=n_gen, omega=0.7298, eta1=2.05, eta2=2.05, max_vel=0.5, variant=5, neighb_type=4, neighb_param=4, memory=False, seed=1234))

    # pso from slides
    udas.append(
        pg.pso(gen=n_gen, omega=0.7298, eta1=1.49618, eta2=1.49618, memory=True, seed=1234, max_vel=0.5, variant=5,
               neighb_type=2))

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

    P = used_parameters
    global_results = []
    print namestr(P, globals())
    par_name = namestr(P, globals())[0]

    print "Starting servers"
    servers = []
    for i in range(n_servers):
        servers.append(ServerTorcs.ServerTorcs(port=3001 + i + offset))
        servers[i].start()
        time.sleep(.5)
    print "Servers started"

    for index, uda in enumerate(udas):
        logs = []
        algo = pg.algorithm(uda)
        new_algo_name = algo.get_name().replace(" ", "").replace(":", "")
        results_trial = []

        time.sleep(1)
        print ('uda:', index)

        for i in range(0, n_trials):
            # prob1 = pg.problem(myProblem(n_servers, index))
            prob1 = pg.problem(
                myProblem(n_servers, index, par_name, n_gen, p_size, datetime.datetime.now().day, new_algo_name,
                          new_parameters, offset))
            # prob1 = pg.problem(myProblemMultiobj(n_servers, index))

            log_trial = []
            algo.set_verbosity(1)
            pop = pg.population(prob1, p_size, seed=i + index)
            algo.evolve(pop)
            log_trial.append(algo.extract(type(uda)).get_log())
            log_trial = np.array(log_trial)
            results_trial.append(np.min(log_trial[:, log_trial.shape[1] - 1, 2]))

        logs.append(algo.extract(type(uda)).get_log())
        logs = np.array(logs)
        avg_log = np.average(logs, 0)
        global_results.append(np.min(results_trial, 0))
        plt.plot(avg_log[:, 1], avg_log[:, 2], label=algo.get_name() + str(index))

        for i, key in enumerate(P):
            P[key] = pop.champion_x[i]

        with open(new_parameters + "_BEST_" + par_name + "_nGen" + str(n_gen) + "_pSize" + str(p_size) + "_circ" + str(
                n_servers) + "_" + new_algo_name + str(index) + "_today" + str(datetime.datetime.now().day) + ".txt",
                  'w') as outfile:
            json.dump(P, outfile)

        with open(
                new_parameters + "_GenBest_" + par_name + "_nGen" + str(n_gen) + "_pSize" + str(p_size) + "_circ" + str(
                        n_servers) + "_" + new_algo_name + str(index) + "_today" + str(
                        datetime.datetime.now().day) + ".txt", 'w') as outfile:
            outfile.write(str(algo.extract(type(uda)).get_log()))

    print("global results: ", global_results)

    for i, key in enumerate(P):
        P[key] = pop.champion_x[i]
    os.chdir(r"C:\Users\Vincenzo\Documents\GitHub\ComputazioneNaturale\snakeoil2015")
    print "champion_x", pop.champion_x
    print "champion_f", pop.champion_f
    with open("def_param.py", 'a') as outfile:
        outfile.write("\n")
        outfile.write(new_parameters + " = " + str(P))
    with open(new_parameters + ".txt", 'w') as outfile:
        json.dump(P, outfile)
    # We then add details to the plot
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    offset = 2

    n_trials = 1
    n_servers = 1
    population_size = 15
    n_gens = 100
    pg.set_global_rng_seed(seed=27)
    new_parameters = "DistanceDamageFitness"
    mySADE(n_trials, n_gens, population_size, new_parameters, n_servers, offset)
