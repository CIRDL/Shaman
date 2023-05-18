# @author Cesar Ramirez
# Optimization model for choosing class schedule
import gurobipy
from gurobipy import *
from num2words import *

# READ DATA FROM EXCEL
import openpyxl as opxl

# Load parameters from Excel file
path = "C:\\dev\\pipe\\CourseConnect\\Schedule-Data.xlsx"
doc = opxl.load_workbook(path)

# ---- Initializations -------------

# Set of classes C
C = []

# Set of semesters
# Assumed, could be updated later with UI
S = tuple([0, 1, 2, 3, 4, 5, 6, 7])

# Parameters

# Credit hours indexed by class c
hrs = {}

# Constants
MIN_HOURS = 12
MAX_HOURS = 20

# Prerequisites list indexed by class c
prereq = {}

# Availability list indexed by class c
avai = {}

# ----------- Read from excel ----------------

ws = doc["ISE Prereqs"]

# Populating classes set C
row = 1
while ws.cell(row=row+1, column=1).value:
    C.append(ws.cell(row=row+1, column=1).value)
    row += 1

# Populating parameter prerequisites prereq
# Indexed by class c first, then prerequisites index i from class order C
row = 1
col = 1
ind_pre = []
while ws.cell(row=row+1, column=col).value:
    ind_pre = []
    while ws.cell(row=row, column=col+1).value or ws.cell(row=row, column=col+1).value == 0:
        ind_pre.append(ws.cell(row=row+1, column=col+1).value)
        col += 1
    prereq[C[row - 1]] = ind_pre
    col = 1
    row += 1


# Populating parameter hours h
ws = doc["ISE"]
row = 1
while ws.cell(row=row+1, column=1).value:
    hrs[C[row-1]] = ws.cell(row=row+1, column=5).value
    row += 1

# Populating parameter avai
ws = doc["ISE Availability"]

row = 1
col = 1
avai = {}
ind_avai = [0, 0, 0, 0, 0, 0, 0, 0]
while ws.cell(row=row+1, column=col).value:
    ind_avai = [0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(8):
        ind_avai[i] = ws.cell(row=row+1, column=col+1).value
        col += 1
    avai[C[row-1]] = ind_avai
    col = 1
    row += 1

# ---------- OPTIMIZATION MODEL ----------------------
# Model
model = Model("Schedule")
model.setParam(GRB.Param.OutputFlag, 0)

# Decision Variables

# sched - first index will be the semester (int) and the second term will be class name (string)
# 1 for taking class at class c at semester s, 0 otherwise
sched = {s: model.addVars(C, name="x", vtype=GRB.BINARY) for s in S}

# bound - single integer variable that represents the highest number of hours that will be required in a semester
# Implicitly accounts for the min and max number of hours per semester to be a full time student
# bounds = model.addVars(S, vtype=GRB.INTEGER, lb=MIN_HOURS, ub=MAX_HOURS, name="bounds")
bound = model.addVar(vtype=GRB.INTEGER, lb=MIN_HOURS, ub=MAX_HOURS, name="bound")

# Constraints

# Configuring bound constraint
model.addConstrs(quicksum(sched[s][c]*hrs[c] for c in C) <= bound for s in S)

# Maintain minimum number of hours for full time student constraint
model.addConstr(bound <= MAX_HOURS)

# model.addConstrs(quicksum(sched[s][c] for c in C) >= MIN_HOURS for s in S)

# Take each required class
model.addConstrs(quicksum(sched[s][c] for s in S) == 1 for c in C)

# Availability constraint
model.addConstrs(sched[i][j] <= avai[j][i] for i in S for j in C)

# Prerequisite constraint
# model.addConstrs(quicksum(sched[k][C[p]] for k in range(s)) <= prereq[c][p] for p in range(len(C))
#                  for c in C for s in S)

# Objective function
model.setObjective(bound, sense=GRB.MINIMIZE)
model.setParam("OutputFlag", 0)

model.update()
model.optimize()

hour_count = 0

# Printing outputs
if model.status == GRB.OPTIMAL:
    print("\nMaximum number of hours required:", model.objVal)
    print("---Schedule---")
    for s in S:
        print(f"{num2words(s+1, to='ordinal').capitalize()} semester:")
        for c in C:
            if sched[s][c] is True:
                hour_count += hrs[c]
                print(f"{c}: {hrs[c]}")
        print("Total hours: ", hour_count)
    hour_count = 0
else:
    print("Not possible :(")
