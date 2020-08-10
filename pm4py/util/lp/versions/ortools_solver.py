import sys
import tempfile
import numpy as np

from ortools.linear_solver import pywraplp
from pm4py.util.lp.parameters import Parameters
from pm4py.util import exec_utils


MIN_THRESHOLD = 10 ** -12


def apply(c, Aub, bub, Aeq, beq, parameters=None):
    """
    Gets the overall solution of the problem

    Parameters
    ------------
    c
        c parameter of the algorithm
    Aub
        A_ub parameter of the algorithm
    bub
        b_ub parameter of the algorithm
    Aeq
        A_eq parameter of the algorithm
    beq
        b_eq parameter of the algorithm
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    sol
        Solution of the LP problem by the given algorithm
    """
    if parameters is None:
        parameters = {}

    require_ilp = exec_utils.get_param_value(Parameters.REQUIRE_ILP, parameters, False)

    Aub = np.asmatrix(Aub)
    if type(bub) is list and len(bub) == 1:
        bub = bub[0]
    if Aeq is not None:
        Aeq = np.asmatrix(Aeq)
    if beq is not None and type(beq) is list and len(beq) == 1:
        beq = beq[0]

    solver = pywraplp.Solver('LinearProgrammingExample',
                             pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    solver.Clear()
    solver.SuppressOutput()

    x_list = []
    for i in range(Aub.shape[1]):
        if require_ilp:
            x = solver.IntVar(-solver.infinity(), solver.infinity(), "x_" + str(i))
        else:
            x = solver.NumVar(-solver.infinity(), solver.infinity(), "x_" + str(i))
        x_list.append(x)

    objective = solver.Objective()
    for j in range(len(c)):
        if abs(c[j]) > MIN_THRESHOLD:
            objective.SetCoefficient(x_list[j], c[j])

    for i in range(Aub.shape[0]):
        ok = False
        for j in range(Aub.shape[1]):
            if abs(Aub[i, j]) > MIN_THRESHOLD:
                ok = True
                break
        if ok:
            constraint = solver.Constraint(-solver.infinity(), bub[i].reshape(-1, ).tolist()[0][0])
            for j in range(Aub.shape[1]):
                if abs(Aub[i, j]) > MIN_THRESHOLD:
                    constraint.SetCoefficient(x_list[j], Aub[i, j])

    if Aeq is not None and beq is not None:
        for i in range(Aeq.shape[0]):
            ok = False
            for j in range(Aeq.shape[1]):
                if abs(Aeq[i, j]) > MIN_THRESHOLD:
                    ok = True
                    break
            if ok:
                constraint = solver.Constraint(beq[i].reshape(-1,).tolist()[0][0], beq[i].reshape(-1,).tolist()[0][0])
                for j in range(Aeq.shape[1]):
                    if abs(Aeq[i, j]) > MIN_THRESHOLD:
                        constraint.SetCoefficient(x_list[j], Aeq[i, j])

    objective.SetMinimization()

    status = solver.Solve()

    if status == 0:
        sol_value = 0.0
        for j in range(len(c)):
            if abs(c[j]) > MIN_THRESHOLD:
                sol_value = sol_value + c[j] * x_list[j].solution_value()
        points = [x.solution_value() for x in x_list]
    else:
        return None

    return {"c": c, "x_list": x_list, "sol_value": sol_value, "points": points}


def get_prim_obj_from_sol(sol, parameters=None):
    """
    Gets the primal objective from the solution of the LP problem

    Parameters
    -------------
    sol
        Solution of the ILP problem by the given algorithm
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    prim_obj
        Primal objective
    """
    if parameters is None:
        parameters = {}

    if sol is not None:
        return sol["sol_value"]


def get_points_from_sol(sol, parameters=None):
    """
    Gets the points from the solution

    Parameters
    -------------
    sol
        Solution of the LP problem by the given algorithm
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    points
        Point of the solution
    """
    if parameters is None:
        parameters = {}

    maximize = parameters["maximize"] if "maximize" in parameters else False
    return_when_none = parameters["return_when_none"] if "return_when_none" in parameters else False
    var_corr = parameters["var_corr"] if "var_corr" in parameters else {}

    if sol is not None:
        return sol["points"]
    else:
        if return_when_none:
            if maximize:
                return [sys.float_info.max] * len(list(var_corr.keys()))
            return [sys.float_info.min] * len(list(var_corr.keys()))

