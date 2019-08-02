import sys
import tempfile
import numpy as np

from ortools.linear_solver import pywraplp

MIN_THRESHOLD = 10 ** -12


def apply(c, Aub, bub, Aeq, beq, parameters=None):
    if parameters is None:
        parameters = {}

    Aub = np.asmatrix(Aub)
    if type(bub) is list and len(bub) == 1:
        bub = bub[0]
    if Aeq is not None:
        Aeq = np.asmatrix(Aeq)
    if beq is not None and type(beq) is list and len(beq) == 1:
        beq = beq[0]

    solver = pywraplp.Solver('LinearProgrammingExample',
                             pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

    x_list = []
    for i in range(Aub.shape[1]):
        x = solver.NumVar(-solver.infinity(), solver.infinity(), "x_" + str(i))
        x_list.append(x)

    objective = solver.Objective()
    for j in range(len(c)):
        if abs(c[j]) > MIN_THRESHOLD:
            objective.SetCoefficient(x[j], c[j])

    for i in range(Aub.shape[0]):
        ok = False
        for j in range(Aub.shape[1]):
            if abs(Aub[i, j]) > MIN_THRESHOLD:
                ok = True
                break
        if ok:
            constraint = solver.Constraint(-solver.infinity(), bub[i])
            for j in range(Aub.shape[1]):
                if abs(Aub[i, j]) > MIN_THRESHOLD:
                    constraint.SetCoefficient(x_list[j], Aub[i][j])

    if Aeq is not None and beq is not None:
        for i in range(Aeq.shape[0]):
            ok = False
            for j in range(Aeq.shape[1]):
                if abs(Aeq[i, j]) > MIN_THRESHOLD:
                    ok = True
                    break
            if ok:
                constraint = solver.Constraint(-solver.infinity(), beq[i])
                for j in range(Aeq.shape[1]):
                    if abs(Aeq[i, j]) > MIN_THRESHOLD:
                        constraint.SetCoefficient(x_list[j], Aeq[i][j])

    objective.SetMinimization()

    solver.Solve()

    return {"c": c, "x_list": x_list}


def get_prim_obj_from_sol(sol, parameters=None):
    if parameters is None:
        parameters = {}

    c = sol["c"]
    x_list = sol["x_list"]

    sol_value = 0.0
    for j in range(len(c)):
        if abs(c[j]) > MIN_THRESHOLD:
            sol_value = sol_value + c[j] * x_list[j].solution_value()

    return sol_value


def get_points_from_sol(sol, parameters=None):
    if parameters is None:
        parameters = {}

    c = sol["c"]
    x_list = sol["x_list"]

    return [x.solution_value() for x in x_list]
