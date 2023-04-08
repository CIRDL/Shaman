# @author Cesar Ramirez
# Optimization model for choosing class schedule


from gurobipy import *

# READ DATA FROM EXCEL
import openpyxl as opxl

# Load parameters from Excel file
path = "C:\\Research\\WebScraping\\Schedule-Data.xlsx"
doc = opxl.load_workbook(path)

# ---- Initializations -------------

# Set of classes C
C = []

# Cleaner:
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
row = 1
col = 1
ind_pre = []
while ws.cell(row=row, column=col+1).value:
    ind_pre = []
    while ws.cell(row=row+1, column=col+1).value or ws.cell(row=row+1, column=col+1).value == 0:
        ind_pre.append(ws.cell(row=row+1, column=col+1).value)
        row += 1
    prereq[C[col - 1]] = ind_pre
    row = 1
    col += 1

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

# Variables
sched = {c: model.addVars(S, name="x", vtype=GRB.BINARY) for c in C}

# Constraints

# Meeting credit hour requirements
model.addConstrs(quicksum(sched[i][j]*hrs[i] for j in S) >= MIN_HOURS for i in C)
model.addConstrs(quicksum(sched[i][j]*hrs[i] for j in S) <= MAX_HOURS for i in C)

# Take each required class
model.addConstrs(quicksum(sched[i][j] for j in S) == 1 for i in C)

# Availability constraint
model.addConstrs(sched[i][j] <= avai[i][j] for i in C for j in S)

# Prerequisite constraint
# model.addConstrs(quicksum(sched[C[k]][sp] for sp in S) >= prereq[i][k] for k in range(len(C)) for i in C for j in S)

# Objective function
model.setObjective(quicksum(quicksum(quicksum(sched[i][j]*hrs[i])/len(S) for i in C) for j in S
                            - quicksum(sched[i][k]*hrs[i]) for i in C) for k in S)

# Tweak model
model.modelSense = GRB.MINIMIZE
model.update()
model.setParam("OutputFlag", 0)

# Optimize model
model.optimize()

scrape = []

# Printing outputs
if model.status == GRB.OPTIMAL:
    print("\nOptimal value:", model.objVal)
    print("--- Quantities---")
    for v in model.getVars():
        if v.x == True and v.varName[0] == "x":
            print("%s: %g" % (v.varName, v.x))
            scrape.append(v.varName[8:14])
else:
    print("No solution")
