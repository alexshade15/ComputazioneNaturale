import pygmo as pg
import numpy as np
import json

jason = open('default_parameters','r')
j = jason.read()
y = json.loads(j)

LOWER_VECTOR = []
UPPER_VECTOR = []
for elem in y:
    UPPER_VECTOR.append(y[elem]+y[elem]*10/100)
    LOWER_VECTOR.append(y[elem]-y[elem]*10/100)


class testProblem:
    def fitness(self, dv):
        return [dv]
    def get_bounds(self):
        return (LOWER_VECTOR, UPPER_VECTOR)


# prob = pg.problem(pg.schwefel(30))
#
# algo = pg.algorithm(pg.de(gen=1000, variant=7, F=0.6, CR=0.9, seed=1234))
#
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