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

import pulp
from pulp import LpProblem, LpMinimize, LpVariable, LpStatus, value

from pm4py.util import exec_utils

from enum import Enum


class Parameters(Enum):
    REQUIRE_ILP = "require_ilp"


MIN_THRESHOLD = 10 ** -12
# max safe number of constraints (log10)
MAX_NUM_CONSTRAINTS = 7

# keeps compatibility with 1.6.x versions of PuLP in which the interface
# for solving was the latter one
if hasattr(pulp, "__version__"):
    # new interface
    from pulp import PULP_CBC_CMD

    solver = lambda prob: PULP_CBC_CMD(msg=0).solve(prob)
else:
    # old interface
    solver = lambda prob: prob.solve()


def get_terminal_part_name_num(num):
    """
    Gets the terminal part of the name of a variable

    Parameters
    ---------------
    nam
        Name

    Returns
    ---------------
    stru
        String
    """
    ret = str(num)
    while len(ret) < MAX_NUM_CONSTRAINTS:
        ret = "0" + ret
    return ret


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

    prob = LpProblem("", LpMinimize)

    x_list = []
    for i in range(Aub.shape[1]):
        if require_ilp:
            x_list.append(LpVariable("x_" + get_terminal_part_name_num(i), cat='Integer'))
        else:
            x_list.append(LpVariable("x_" + get_terminal_part_name_num(i)))

    eval_str = ""
    expr_count = 0
    min_threshold = min(max(c[j] for j in range(len(c))), MIN_THRESHOLD)
    for j in range(len(c)):
        if abs(c[j]) >= min_threshold:
            if expr_count > 0:
                eval_str = eval_str + " + "
            eval_str = eval_str + str(c[j]) + "*x_list[" + str(j) + "]"
            expr_count = expr_count + 1
    eval_str = eval_str + ", \"objective\""
    prob += eval(eval_str)

    min_threshold = min(max(Aub[i, j] for i in range(Aub.shape[0]) for j in range(Aub.shape[1])), MIN_THRESHOLD)
    for i in range(Aub.shape[0]):
        expr_count = 0
        eval_str = 0
        eval_str = ""
        for j in range(Aub.shape[1]):
            if abs(Aub[i, j]) >= min_threshold:
                if expr_count > 0:
                    eval_str = eval_str + " + "
                eval_str = eval_str + str(Aub[i, j]) + "*x_list[" + str(j) + "]"
                expr_count = expr_count + 1
        if eval_str:
            eval_str = eval_str + "<=" + str(
                bub[i]) + ", \"vinc_" + get_terminal_part_name_num(i) + "\""

            prob += eval(eval_str)

    if Aeq is not None and beq is not None:
        for i in range(Aeq.shape[0]):
            expr_count = 0
            eval_str = 0
            eval_str = ""
            for j in range(Aeq.shape[1]):
                if abs(Aeq[i, j]) > MIN_THRESHOLD:
                    if expr_count > 0:
                        eval_str = eval_str + " + "
                    eval_str = eval_str + str(Aeq[i, j]) + "*x_list[" + str(j) + "]"
                    expr_count = expr_count + 1
            if eval_str:
                eval_str = eval_str + "==" + str(
                    beq[i]) + ", \"vinceq_" + get_terminal_part_name_num(
                    i + 1 + Aub.shape[0]) + "\""

                prob += eval(eval_str)

    filename = tempfile.NamedTemporaryFile(suffix='.lp')
    filename.close()
    prob.writeLP(filename.name)
    solver(prob)

    return prob


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

    return value(sol.objective)


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

    if str(LpStatus[sol.status]) == "Optimal":
        x_i = []
        for v in sol.variables():
            x_i.append(v.varValue)
        return x_i
    else:
        if return_when_none:
            if maximize:
                return [sys.float_info.max] * len(list(var_corr.keys()))
            return [sys.float_info.min] * len(list(var_corr.keys()))
