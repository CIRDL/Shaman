# @author Cesar Ramirez
# Optimization model for choosing class schedule


from gurobipy import *
from numpy import max, array

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

# Variable - sched is indexed as semester x classes
# This means that the first index will be the semester (int) and the second term will be class name (string)
sched = {s: model.addVars(C, name="x", vtype=GRB.BINARY) for s in S}

# TODO - need to fix everything since I switched the order of the indexes

# Somehow trying to find the max and min semesters by hour for the objective function
semester_hours_list = []
for s in S:
    semester_hours_list.append(sched[s].sum())

semester_hours = array(semester_hours_list)

# Constraints

# Meeting credit hour requirements
model.addConstrs(quicksum(sched[i][j]*hrs[i] for j in C) >= MIN_HOURS for i in S)
model.addConstrs(quicksum(sched[i][j]*hrs[i] for j in C) <= MAX_HOURS for i in S)

# Take each required class
model.addConstrs(quicksum(sched[i][j] for j in C) == 1 for i in S)

# Availability constraint
model.addConstrs(sched[i][j] <= avai[i][j] for i in S for j in C)

model.update()

# max_hrs = 0
# max_sem = 0
# for s in S:
#     cur_hrs = 0
#     for c in C:
#         cur_hrs += sched[c][s]
#         print(sched[c][s])
#     if max_hrs < cur_hrs:
#         max_sem = s
#         max_hrs = cur_hrs
# print(max_sem)
print(sched)

# ----------------------------- Blocked out code

# Prerequisite constraint
# model.addConstrs(quicksum(sched[C[k]][sp] for sp in S) >= prereq[i][k] for k in range(len(C)) for i in C for j in S)

# Objective function
# model.setObjective(quicksum(quicksum(quicksum(sched[i][j]*hrs[i])/len(S) for i in C) for j in S
#                             - quicksum(sched[i][k]*hrs[i]) for i in C) for k in S)

# # Tweak model
# model.modelSense = GRB.MINIMIZE
# model.update()
# model.setParam("OutputFlag", 0)
#
# # Optimize model
# model.optimize()
#
# scrape = []
#
# # Printing outputs
# if model.status == GRB.OPTIMAL:
#     print("\nOptimal value:", model.objVal)
#     print("--- Quantities---")
#     for v in model.getVars():
#         if v.x is True and v.varName[0] == "x":
#             print("%s: %g" % (v.varName, v.x))
#             scrape.append(v.varName[8:14])
# else:
#     print("No solution")
