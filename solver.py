import collections
import operator
import numpy as np
import math
import random


class SolverConfig:
    greenw = 0.2
    costw = 0.2
    productivityw = 0.2
    delayw = 0.2
    success_ratew = 0.2



class Edge:
    def __init__(self, fleet, customer, value):
        self.fleet = fleet
        self.customer = customer
        self.value = value




class Solver:

    def __init__(self, problem, config):
        self.problem = problem
        self.config = config

        areas = problem.areas
        marginal_productivities = problem.marginal_productivities
        marginal_delays = problem.delays
        marginal_success_rates = problem.marginal_success_rates
        marginal_costs = problem.costs
        marginal_green_capacities = problem.marginal_green_capacities

        # create edges
        edges = collections.deque()
        values_matrix = np.zeros(marginal_productivities.shape)
        for fleet in problem.fleets:
            for customer in problem.customers:
                if areas[customer.id, fleet.id] == 1:
                    value = config.greenw * marginal_green_capacities[fleet.id]
                    value += config.productivityw * marginal_productivities[customer.id, fleet.id]
                    value += config.success_ratew * marginal_success_rates[customer.id, fleet.id]
                    value -= config.delayw * marginal_delays[customer.id, fleet.id]
                    value -= config.costw * marginal_costs[fleet.id]
                    edges.append(Edge(fleet, customer, value=value))
                    print(value)
                    values_matrix[customer.id, fleet.id] = value
        self.edges = edges
        self.values_matrix = values_matrix

    @staticmethod
    def reset_fleet(fleet):
        fleet.customers = collections.deque()
        fleet.capacity_level = 0
        fleet.volume_level = 0
        return fleet

    @staticmethod
    def reset_customer(customer):
        customer.assigned = False
        customer.assigned_qty = 0
        return customer

    @staticmethod
    def biased_randomisation (array, beta):
        L = len(array)
        options = list(array)
        for _ in range(L):
            idx = int(math.log(random.random(), 1.0 - beta)) % len(options)
            yield options.pop(idx)


    def evaluate(self, assignments):
        return (assignments * self.values_matrix).sum()


    def run_capacity_constrained (self, beta=0.9999):
        fleets, customers = self.problem.fleets, self.problem.customers
        # Create the savings list
        savings_list = sorted(self.edges, key=operator.attrgetter("value"), reverse=True)

        # Reset the current solution
        fleets = list(map(self.reset_fleet, fleets))
        customers = list(map(self.reset_customer, customers))

        # Init assignments matrix
        assignments = np.zeros(self.problem.productivities.shape).asype("int32")

        # Construct a solution
        for edge in self.biased_randomisation(savings_list, beta):
            fleet, customer = edge.fleet, edge.customer
            if customer.assigned:
                continue

            if fleet.capacity_level + customer.demand < fleet.maxcapacity:
                customer.assigned = True
                fleet.customers.append(customer)
                fleet.capacity_level += customer.demand
                customer.assigned_qty = customer.demand
                assignments[customer.id, fleet.id] += 1

        return assignments


    def multistart (self, maxiter=3000):
        current_sol = self.run_capacity_constrained(beta=0.9999)
        current_value = self.evaluate(current_sol)
        for _ in range(maxiter):
            ibeta = random.uniform(0.1, 0.3)
            new_sol = self.run_capacity_constrained(beta=ibeta)
            new_value = self.evaluate(new_sol)
            if new_value > current_value:
                current_sol, current_value = new_sol, new_value
        return current_sol


    def run_volume_constrained (self, beta=0.9999):
        fleets, customers = self.problem.fleets, self.problem.customers
        # Create the savings list
        savings_list = sorted(self.edges, key=operator.attrgetter("value"), reverse=True)

        # Reset the current solution
        fleets = list(map(self.reset_fleet, fleets))
        customers = list(map(self.reset_customer, customers))

        # Init assignments matrix
        assignments = np.zeros(self.problem.productivities.shape).astype("float32")

        # Possible further loop for ensuring the respect of minimum volume constrain
        # ...
        """
        for fleet in fleets:
            for edge in savings_list:
                customer = edge.customer
                # Only considers fleets one by one
                if edge.fleet != fleet:
                    continue
                # if minimum volume is fulfilled, go to next fleet
                if fleet.volume_level >= fleet.minvolume:
                    break
                # If customer is a lready fulfilled go to next edge
                if customer.assigned_qty >= customer.demand:
                    continue
                # Assign a certain quantity
                assigned_qty = min(customer.demand - customer.assigned_qty, fleet.minvolume - fleet.volume_level)
                fleet.customers.append((customer, assigned_qty, ))
                fleet.volume_level += assigned_qty
                customer.assigned_qty += assigned_qty
                assignments[customer.id, fleet.id] += round(assigned_qty / customer.demand, 2)
        """

        # Construct a solution
        for edge in self.biased_randomisation(savings_list, beta):
            fleet, customer = edge.fleet, edge.customer
            if customer.assigned_qty >= customer.demand:
                continue

            if fleet.volume_level < fleet.maxvolume:
                #customer.assigned = True
                assigned_qty = min(customer.demand - customer.assigned_qty, fleet.maxvolume - fleet.volume_level)
                fleet.customers.append((customer, assigned_qty, ))
                fleet.volume_level += assigned_qty
                customer.assigned_qty += assigned_qty
                assignments[customer.id, fleet.id] += round(assigned_qty / customer.demand, 2)

        return assignments
