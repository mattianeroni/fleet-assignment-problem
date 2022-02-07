import utils
from solver import Solver, SolverConfig


problem = utils.read_problem()

config = SolverConfig()
solver = Solver(problem, config)
solution = solver.run_volume_constrained()

print(solution)

for fleet in problem.fleets:
    print("Assigned Qty : ", sum(i[1] for i in fleet.customers))
    print("Min Qty : ", fleet.minvolume)

#print(solution.sum(axis=1))
#print(utils.solution_to_dataframe(solution))
