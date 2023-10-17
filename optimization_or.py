from ortools.linear_solver import pywraplp
import logging
from ingest_data import *


# Configure logging
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

# Create the mip solver with the SCIP backend.
solver = pywraplp.Solver.CreateSolver("SAT")
if not solver:
    logging.debug('No solver')

# Define the variables

# x and y are integer non-negative variables.
x = solver.IntVar(0.0, infinity, "x")
y = solver.IntVar(0.0, infinity, "y")

print("Number of variables =", solver.NumVariables())

# Define the constraints
# x + 7 * y <= 17.5.
solver.Add(x + 7 * y <= 17.5)

# x <= 3.5.
solver.Add(x <= 3.5)

print("Number of constraints =", solver.NumConstraints())

# Define the objective
# Maximize x + 10 * y.
solver.Maximize(x + 10 * y)

# Call the solver
print(f"Solving with {solver.SolverVersion()}")
status = solver.Solve()

# Display solution
if status == pywraplp.Solver.OPTIMAL:
    print("Solution:")
    print("Objective value =", solver.Objective().Value())
    print("x =", x.solution_value())
    print("y =", y.solution_value())
else:
    print("The problem does not have an optimal solution.")
