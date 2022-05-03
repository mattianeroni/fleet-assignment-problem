"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
This project concerns the development of a set of algorithms for solving the fleet 
assignment problem under additional constraints:
    - Limited capacity of fleets
    - Minimum load for fleets
    - Green capacity of fleets
    - Stochastic productivity
    
This problem is completely new in scientific literature and the proposed solutions 
are supporteed and validated by a case study based on real data. 


Author: Mattia Neroni, Ph.D., Eng.
Contact: mneroni@uoc.edu
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
import time 

import utils 
import nigeria



if __name__ == "__main__":

    problem = utils.read_problem()

    print("Time, DeterministicCost, StochasticCost, " * 2)



    # Deterministic version of the genetic algorithm

    solver = nigeria.GA(psize=30, co=0.75, mut=0.05, maxiter=2000, beta=0.6)

    start_time = time.time()

    solution = solver.run(problem, simulation=(False, 50))

    duration = round(time.time() - start_time, 3)

    cost = round(nigeria.evaluate_process(solution, problem), 3)
    
    stochastic_cost = round(nigeria.evaluate_process(solution, problem, (True, 100)), 3) 

    print(f"{duration}, {cost}, {stochastic_cost}", end=", ")



    # Stochastic version of the genetic algorithm 

    solver = nigeria.GA(psize=30, co=0.75, mut=0.05, maxiter=2000, beta=0.6)

    start_time = time.time()

    solution = solver.run(problem, simulation=(True, 50))

    duration = round(time.time() - start_time, 3)

    cost = round(nigeria.evaluate_process(solution, problem), 3)
    
    stochastic_cost = round(nigeria.evaluate_process(solution, problem, (True, 100)), 3) 

    print(f"{duration}, {cost}, {stochastic_cost}", end=", ")


    
    
    print("\nWell done \U0001F49A !")