'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import sys
import tempfile
import numpy as np

from ortools.linear_solver import pywraplp
from pm4py.util import exec_utils

from enum import Enum


class Parameters(Enum):
    REQUIRE_ILP = "require_ilp"


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
            constraint = solver.Constraint(-solver.infinity(), bub[i])
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
                constraint = solver.Constraint(beq[i], beq[i])
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

