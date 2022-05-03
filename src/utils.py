"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
This project concerns the development of a set of algorithms for solving the fleet 
assignment problem under additional constraints:
    - Limited capacity of fleets
    - Minimum load for fleets
    - Discounts
    - Stochastic productivity
    
This problem is completely new in scientific literature and the proposed solutions 
are supporteed and validated by a case study based on real data. 


Author: Mattia Neroni, Ph.D., Eng.
Contact: mneroni@uoc.edu
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
import pandas as pd 
import numpy as np 
import functools 
import itertools





class Problem:

    def __init__(self, avail, demand, costs, maxcap, mincap, discount, prods, stdev):
        """
        Initialise.

        :param avail: A matrix of available assignments.
        :param demand: The demand for each postcode.
        :param costs: The costs per hour of fleets.
        :param maxcap: The maximum capacities of fleets.
        :param mincap: The minimum capacities of fleets.
        :param discount: The discount applied to each fleet.
        :param prods: The productivity of each vehicle in each postcode expressed in parcels per hour.
        :param stdev: Possible deviations calculated on historical delays data.

        :attr n_fleets: The number of fleets.
        :attr n_postcodes: The number of postcodes.
        """
        self.n_postcodes, self.n_fleets = avail.shape
        self.avail = avail
        self.demand = demand
        self.costs = costs 
        self.maxcap = maxcap
        self.mincap = mincap
        self.discount = discount
        self.prods = prods 
        self.stdev = stdev

        # Some corrections because of the error in numpy library
        # to calculate the stochastic productivity with a lognormal
        var = stdev * prods
        phi = np.sqrt(var + prods**2)
        mu = np.log( prods**2 / phi )
        sigma = np.sqrt(np.log( phi**2 / prods**2 ))
        self.stochastic_prods = functools.partial(np.random.lognormal, mean=mu, sigma=sigma)

        # A set of iterators on the fleets that is possible to assign to each postcode
        self.avail_assignments = tuple( itertools.cycle(np.where(avail[i] == 1)[0]) for i in range(self.n_postcodes))



    def __hash__(self):
        return id(self)



def read_problem (path="../data/", max_stdev=0.5):
    """
    Mathod used to read the case study problem.

    :param path: The directory where all the csv can be found.
    :param max_stdev: The maximum standard deviation on stochastic data (i.e., demand and productivity).
    """
    avail = pd.read_csv(path + "FleetAreaConstraints.csv", index_col=0).to_numpy().astype("int32")
    demand = pd.read_csv(path + "Demand.csv", index_col=0).to_numpy().astype("int32")

    fleets_df = pd.read_csv(path + "Fleets.csv", index_col=0)
    costs = fleets_df.loc["cost"].to_numpy().astype("float32")
    maxcap = fleets_df.loc["maxcapacity"].to_numpy().astype("int32")
    mincap = fleets_df.loc["mincapacity"].to_numpy().astype("int32")
    discount = fleets_df.loc["greencapacity"].to_numpy().astype("int32")

    prods = pd.read_csv(path + "ParcelsPerH.csv", index_col=0).to_numpy().astype("float32")
    stdev = pd.read_csv(path + "Delayed.csv", index_col=0).to_numpy().astype("float32") * max_stdev

    return Problem(avail, demand, costs, maxcap, mincap, discount, prods, stdev)