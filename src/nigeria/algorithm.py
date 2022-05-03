import numpy as np 
import random 
import math 
import statistics
import functools
import itertools 




def sol_to_binary(solution, problem):
    """
    Transform the solution in a binary matrix (postcodes, fleets)

    :param solution: The solution as an array of fleets
    :param problem: The problem instance to solve
    """
    bsol = np.zeros((problem.n_postcodes, problem.n_fleets))
    for postcode, fleet in enumerate(solution):
        bsol[postcode, fleet] = 1

    return bsol 



def check_feasibility (bsol, problem, simulation=(False, 50)):
    """
    This method checks the feasibility of a solution.

    :param bsol: The solution expressed with a binary matrix 
    :param problem: The instance of problem

    :param simulation: NOT USED RIGHT NOW (to use in case of stochastic demand)    

    """
    # Check the feasibilities 
    feasible = (bsol * problem.avail).sum() == problem.n_postcodes
    if not feasible:
        return False

    # Check the capacity constraints 
    delivery_qties = (bsol * problem.demand).sum(axis=0)
    feasible = all(delivery_qties >= problem.mincap) and all(delivery_qties <= problem.maxcap)
    if not feasible:
        return False
    
    # Eventual feasibility
    return True




def evaluate (bsol, problem):
    """
    Evaluate a solution in a deterministic way.

    :param bsol: The solution expressed with a binary matrix 
    :param problem: The instance of problem
    """
    # Calculate the quantities each fleet collect from each postcode
    qties = bsol * problem.demand 
    
    # Calculate the time needed for the collection
    hours = qties / problem.prods 

    # Calculate the total cost 
    cost = (hours.sum(axis=0) * problem.costs).sum()

    # Calculate the discount
    discount = (np.minimum(qties.sum(axis=0), problem.discount) * problem.costs).sum()

    # Return the total cost 
    return max(0, cost - discount)



def simulate (bsol, problem, maxiter):
    """
    Like evaluate but runs a short simulation to 
    evaluate the solution in a stochastic way.

    :param bsol: The solution expressed with a binary matrix 
    :param problem: The instance of problem
    :param maxiter: The number of iterations of the Montecarlo simulation
    """
    # Calculate the quantities each fleet collect from each postcode
    qties = bsol * problem.demand

    # Compute the discount 
    discount = (np.minimum(qties.sum(axis=0), problem.discount) * problem.costs).sum()

    # Short montecarlo simulation 
    costs = [None] * maxiter 
    for i in range(maxiter):
        hours = qties / problem.stochastic_prods()
        stochastic_costs = hours.sum(axis=0) * problem.costs 
        costs[i] = max(0, stochastic_costs.sum() - discount)

    # Return the average cost registered during the simulations
    return statistics.mean(costs)
    


#@functools.lru_cache(maxsize=None)
def evaluate_process (solution, problem, simulation=(False, 50)):
    """
    A short cut for doing all together:
    -   transformation of the solution in a binary matrix 
    -   feasibility check 
    -   evaluation 

    :param solution: The solution expressed as a list of fleets 
    :param problem: The instance of problem to solve
    :param simulation: The characteristics of the simulation (DoOrNot, Iterations)
    """
    # Simulation characteristics 
    sim, maxiter = simulation 

    # Trnasform solution to binary matrix and check feasibility
    bsol = sol_to_binary(solution,problem)
    feasible = check_feasibility(bsol, problem)

    # If the solution is not feasible it will have a very high cost.
    if not feasible:
        return float("inf")
    
    if sim:
        return simulate(bsol, problem, maxiter)
    
    return evaluate(bsol, problem)
    


def bra (options, beta):
    """
    A biased randomised selection over a set of possible options
    using a quasi-geometric function defined by the parameter beta.

    :param options: The possible options.
    :param beta: The parameter of the geometric function.
    """
    options = list(options)
    L = len(options)
    for _ in range(L):
        idx = int(math.log(random.random(), 1.0 - beta)) % len(options)
        yield options.pop(idx)




class GA:
    """
    An instance of this class represents the proposed 
    Simulation-Based Genetic Algorithm.
    """

    def __init__(self, psize=20, co=0.75, mut=0.05, maxiter=1000, beta=0.4):
        """
        Initialise.

        :param psize: The population size.
        :param co: The changeover probability
        :param mut: The mutation probability 
        :param maxiter: The number of iterations 
        :param beta: The parameter of the biased randomised selection.
        """
        self.psize = psize 
        self.co = co 
        self.mut = mut 
        self.maxiter = maxiter 
        self.beta = beta 

    def run (self, problem, simulation=(False, 50)):
        """
        This method is the main execution of the algorithm.
        :param problem: The instance of problem to solve.
        :param simulation: The characteristics of the simulation (DoOrNot, Iterations)
        """
        # Characteristics of the problem 
        n_postcodes, n_fleets = problem.n_postcodes, problem.n_fleets
        co, mut = self.co, self.mut
        avail_assignments = problem.avail_assignments

        # Init a random population
        population = [ np.random.randint(0, n_fleets, size=(n_postcodes)) for _ in range(self.psize)]

        for i in range(self.maxiter):
        
            # Sort from best to worst 
            population.sort(key=lambda i: evaluate_process(tuple(i), problem, simulation))
            
            # Init the solutions selector 
            selector = bra(population, self.beta)

            # Init new population 
            newpop = []

            # Change over
            for _ in range(len(population) // 2):

                # Pick mother and father
                father = next(selector)
                mother = next(selector)

                # CO probabilities
                co_probs = np.random.rand(n_postcodes)
                
                # Create children
                son = np.where(co_probs >= co, mother, father)
                daughter = np.where(co_probs < co, mother, father)

                # Eventual mutation in son and daughter
                for j, (mutson, mutdaughter) in enumerate(zip(np.random.rand(n_postcodes), np.random.rand(n_postcodes))):
                    if mutson < mut:
                        son[j] = next(avail_assignments[j])
                    
                    if mutdaughter < mut:
                        daughter[j] = next(avail_assignments[j])

                #mut_probs = np.random.rand(n_postcodes)
                #son = np.where(mut_probs < mut, son + 1, son)
                #son = np.where(son >= n_fleets, 0, son)

                # Eventual mutation in daughter
                #mut_probs = np.random.rand(n_postcodes)
                #daughter = np.where(mut_probs < mut, daughter + 1, daughter)
                #daughter = np.where(daughter >= n_fleets, 0, daughter)

                # Update new population 
                newpop.extend([son, daughter])

            # Update population 
            population = newpop

        # Return the best, the deterministic cost, and the stochastic cost
        return tuple(min(population, key=lambda i: evaluate_process(tuple(i), problem, simulation)))