"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
This project concerns the development of a set of algorithms for solving the fleet 
assignment problem under additional constraints:
    - Limited capacity of fleets
    - Minimum load for fleets
    - Green capacity of fleets
    - Stochastic demand and stochastic productivity
    
This problem is completely new in scientific literature and the proposed solutions 
are supporteed and validated by a case study based on real data. 


Author: Mattia Neroni, Ph.D., Eng.
Contact: mneroni@uoc.edu
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
import pandas as pd 
import numpy as np 



class Problem:

    def __init__(self, avail, demand, costs, maxcap, mincap, greencap, prods, stdev):
        """
        Initialise.

        :param avail: A matrix of available assignments.
        :param demand: The demand for each postcode.
        :param costs: The costs per parcel of vehicles.
        :param maxcap: The maximum capacities of vehicles.
        :param mincap: The minimum capacities of vehicles.
        :param greencap: The free capacity of vehicles that can be used without
                        involving any cost.
        :param prods: The productivity of each vehicle in each postcode.
        :param stdev: Possible deviations calculated on historical delays data.
        """
        self.avail = avail
        self.demand = demand
        self.costs = costs 
        self.maxcap = maxcap
        self.mincap = mincap
        self.greencap = greencap
        self.prods = prods 
        self.stdev = stdev



def read_problem (path="../data/", max_stdev=0.5):
    """
    Mathod used to read the case study problem.

    :param path: The directory where all the csv can be found.
    :param max_stdev: The maximum standard deviation on stochastic data (i.e., demand and productivity).
    """
    avail = pd.read_csv(path + "FleetAreaConstraints.csv", index_col=0).to_numpy().astype("int32")
    demand = pd.read_csv(path + "Demand.csv", index_col=0).to_numpy().astype("int32")

    fleets_df = pd.read_csv(path + "Fleets.csv", index_col=0)
    costs = fleets_df.loc["cost"].to_numpy().astype("int32")
    maxcap = fleets_df.loc["maxcapacity"].to_numpy().astype("int32")
    mincap = fleets_df.loc["mincapacity"].to_numpy().astype("int32")
    greencap = fleets_df.loc["greencapacity"].to_numpy().astype("int32")

    prods = pd.read_csv(path + "ParcelsPerH.csv", index_col=0).to_numpy().astype("float32")
    stdev = pd.read_csv(path + "Delayed.csv", index_col=0).to_numpy().astype("float32") * max_stdev

    return Problem(avail, demand, costs, maxcap, mincap, greencap, stdev)