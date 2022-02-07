import pandas as pd
import numpy as np
import itertools

import fleet
import customer


class Problem:
    def __init__(self, customers, fleets, areas,
    productivities, delays, success_rates, costs, green_capacities,
    marginal_productivities, marginal_delays, marginal_success_rates, marginal_costs, marginal_green_capacities):
        self.customers = customers
        self.fleets = fleets
        self.areas = areas

        self.productivities = productivities
        self.delays = delays
        self.success_rates = success_rates
        self.costs = costs
        self.green_capacities = green_capacities

        self.marginal_productivities = marginal_productivities
        self.marginal_delays = delays
        self.marginal_success_rates = marginal_success_rates
        self.marginal_costs = costs
        self.marginal_green_capacities = marginal_green_capacities

    def __repr__(self):
        return str(self.__dict__)

def read_problem ():
    # Read demand
    demands = pd.read_csv("./data/Demand.csv", index_col=0)["Parcels"].values
    customers = tuple(customer.Customer(id, d) for id, d in enumerate(demands))
    # Read fleets
    df = pd.read_csv("./data/Fleets.csv", index_col=0).T
    fleets = tuple(
        fleet.Fleet(
            id=id,
            maxshare=f['Max Volume Share in %'],
            maxcapacity =f['Maximum Capacity in parcels'],
            maxvolume = f['Maximum Volume in parcels'],
            minvolume = f['Minimum Volume in parcels'],
        )
    for id, (_, f) in enumerate(df.iterrows()))
    # Read area constraints
    areas = pd.read_csv("./data/FleetAreaConstraints.csv", index_col=0).to_numpy().astype("int32")
    # Read productivity
    productivities = pd.read_csv("./data/ParcelsPerH.csv", index_col=0).to_numpy().astype("float32")
    # Read delays
    delays = pd.read_csv("./data/Delayed.csv", index_col=0).to_numpy().astype("float32")
    # Read success rate
    success_rates = pd.read_csv("./data/DSR.csv", index_col=0).to_numpy().astype("float32")

    # Read green capacities and costs
    df = pd.read_csv("./data/Fleets.csv", index_col=0)
    green_capacities = df.loc['Green Capacity in parcels'].to_numpy().astype("int32")
    costs = df.loc['Cost per Parcel in €'].to_numpy().astype("float32")

    # Calculate the marginal values
    # NOTE: a correction is made to delays to avoid divisions by zero
    delays = np.maximum(delays, 0.001)
    marginal_productivities = np.zeros(productivities.shape).astype("float32")
    marginal_delays = np.zeros(delays.shape).astype("float32")
    marginal_success_rates = np.zeros(success_rates.shape).astype("float32")
    marginal_costs = np.zeros(costs.shape).astype("float32")
    marginal_green_capacities = np.zeros(green_capacities.shape).astype("float32")
    for i, _ in enumerate(fleets):
        marginal_productivities[:,i] = productivities[:,i] / np.concatenate((productivities[:,:i], productivities[:,i+1:],), axis=1).max(axis=1)
        marginal_delays[:,i] = delays[:,i] / np.concatenate((delays[:,:i], delays[:,i+1:],), axis=1).min(axis=1)
        marginal_success_rates[:,i] = success_rates[:,i] / np.concatenate((success_rates[:,:i], success_rates[:,i+1:],), axis=1).max(axis=1)
        marginal_costs[i] = costs[i] / np.concatenate((costs[:i], costs[i+1:], )).min()
        marginal_green_capacities[i] = green_capacities[i] / np.concatenate((green_capacities[:i],green_capacities[i+1:],)).max()

    
    return Problem(
        customers, fleets, areas,
        productivities, delays, success_rates, costs, green_capacities,
        marginal_productivities, marginal_delays, marginal_success_rates, marginal_costs, marginal_green_capacities
    )


def solution_to_dataframe(solution):
    df = pd.read_csv("./data/FleetAreaConstraints.csv", index_col=0)
    for i in range(1, solution.shape[1] + 1):
        df[f"Fleet" + str(i)] = solution[:,i - 1]
    return df.astype("int32")
