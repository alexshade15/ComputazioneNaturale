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

    # pso from slides
    # udas.append(
    #     pg.pso(gen=n_gen, omega=0.7298, eta1=1.49618, eta2=1.49618, memory=True, seed=1234, max_vel=0.5, variant=5,
    #            neighb_type=2))
    #
    # udas.append(pg.sade(gen=n_gen, variant=7, variant_adptv=1, memory=False, seed=1234, ftol=1e-3, xtol=1e-3))
    # udas.append(pg.sade(gen=n_gen, variant=8, variant_adptv=1, memory=False, seed=1234, ftol=1e-3, xtol=1e-3))
    # udas.append(pg.sade(gen=n_gen, variant=18, variant_adptv=1, memory=False, seed=1234, ftol=1e-3, xtol=1e-3))

    # algo = pg.algorithm(pg.gaco(10, 13, 1.0, 1e9, 0.0, 1, 7, 100000, 100000, 0.0, 10, 0.9, False, 23))

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

    plotting = []
    P = used_parameters
    global_results = []
    print namestr(P, globals())
    par_name = namestr(P, globals())[0]
    today = datetime.datetime.now().day

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

        for j in range(0, n_trials):
            # prob1 = pg.problem(myProblem(n_servers, index))
            prob1 = pg.problem(
                myProblem(n_servers, index + j, par_name, n_gen, p_size, today, new_algo_name,
                          new_parameters, offset))
            # prob1 = pg.problem(myProblemMultiobj(n_servers, index))

            log_trial = []
            algo.set_verbosity(1)
            pop = pg.population(prob1, p_size, seed=j + index)
            # pop_inj = [3.15392734e+01, 4.06351818e+03, 4.97105933e+03, 1.21724869e-02,
            #            8.46515570e+03, 4.20830027e+03, 3.36044504e+01, 8.29855857e+02,
            #            7.34442849e+03, 2.31965057e-01, 1.12100314e+02, 8.61982701e-04,
            #            7.69219306e+03, 1.64014121e+00, 9.21010307e+00, 3.05622329e+00,
            #            4.25427737e-02, 5.29581177e+03, 4.43502782e-01, 3.48692685e+01,
            #            6.78188600e+03, 7.64180124e+01, 4.51893080e-01, 1.00028542e-04,
            #            2.55765200e+01, 2.55946953e+00, 1.06115486e-01, 8.31605221e-02,
            #            3.73600771e-01, 5.80222129e-01, 9.95582187e-01, 8.34279341e+03,
            #            1.96224119e+02, 2.47433910e-02, 9.08202495e+00, 2.34373462e+00,
            #            1.72508422e-01, 2.45826790e-01, 1.25945279e+01, 7.14638162e-01,
            #            4.51873959e-01, -3.13286844e-01, 2.71382726e+00, 4.68865255e+02,
            #            2.15839339e+00, 2.91927274e+00, 2.22224571e+00, 1.57180463e+00,
            #            7.34361953e-01, 3.11895138e+03]
            # pop.push_back(pop_inj)
            algo.evolve(pop)
            log_trial.append(algo.extract(type(uda)).get_log())
            log_trial = np.array(log_trial)
            results_trial.append(np.min(log_trial[:, log_trial.shape[1] - 1, 2]))
            # print "trial", j, "--", results_trial
            plotting.append(log_trial)

        logs.append(algo.extract(type(uda)).get_log())
        logs = np.array(logs)
        # print "logs", logs
        avg_log = np.average(logs, 0)
        # print "avg_log", avg_log
        global_results.append(np.min(results_trial, 0))
        plt.plot(avg_log[:, 1], avg_log[:, 2], label=algo.get_name() + str(index))
        if n_trials > 1:
            for j, elem in enumerate(plotting):
                plt.plot(elem[0][:, 1], elem[0][:, 2], label=str(j))

        # print "plotting", plotting
        # print "-------------------"
        # for elem in plotting:
        #     print elem
        #     for ele in elem:
        #         print ele
        #         for el in ele:
        #             print el

        for i, key in enumerate(P):
            P[key] = pop.champion_x[i]

        with open(new_parameters + "_BEST_" + par_name + "_nGen" + str(n_gen) + "_pSize" + str(p_size) + "_circ" + str(
                n_servers) + "_" + new_algo_name + str(index + j) + "_today" + str(today) + ".txt",
                  'w') as outfile:
            json.dump(P, outfile)

        with open(
                new_parameters + "_GenBest_" + par_name + "_nGen" + str(n_gen) + "_pSize" + str(p_size) + "_circ" + str(
                    n_servers) + "_" + new_algo_name + str(index + j) + "_today" + str(
                    today) + ".txt", 'w') as outfile:
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
    if n_trials < 2:
        plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    offset = 0

    n_trials = 5
    n_servers = 3
    population_size = 15
    n_gens = 100
    pg.set_global_rng_seed(seed=27)
    new_parameters = "SADE2_FullFit"
    mySADE(n_trials, n_gens, population_size, new_parameters, n_servers, offset)
