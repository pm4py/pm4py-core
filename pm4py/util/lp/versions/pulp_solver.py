import sys
import tempfile
import numpy as np

from pulp import LpProblem, LpMinimize, LpVariable, LpStatus, value
from pm4py.util.lp.parameters import Parameters
from pm4py.util import exec_utils

MIN_THRESHOLD = 10 ** -12
# max safe number of constraints (log10)
MAX_NUM_CONSTRAINTS = 7


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

    Aub = np.asmatrix(Aub)
    if type(bub) is list and len(bub) == 1:
        bub = bub[0]
    if Aeq is not None:
        Aeq = np.asmatrix(Aeq)
    if beq is not None and type(beq) is list and len(beq) == 1:
        beq = beq[0]

    prob = LpProblem("", LpMinimize)

    x_list = []
    for i in range(Aub.shape[1]):
        if require_ilp:
            x_list.append(LpVariable("x_" + get_terminal_part_name_num(i), cat='Binary'))
        else:
            x_list.append(LpVariable("x_" + get_terminal_part_name_num(i)))

    eval_str = ""
    expr_count = 0
    for j in range(len(c)):
        if abs(c[j]) > MIN_THRESHOLD:
            if expr_count > 0:
                eval_str = eval_str + " + "
            eval_str = eval_str + str(c[j]) + "*x_list[" + str(j) + "]"
            expr_count = expr_count + 1
    eval_str = eval_str + ", \"objective\""
    prob += eval(eval_str)

    for i in range(Aub.shape[0]):
        expr_count = 0
        eval_str = 0
        eval_str = ""
        for j in range(Aub.shape[1]):
            if abs(Aub[i, j]) > MIN_THRESHOLD:
                if expr_count > 0:
                    eval_str = eval_str + " + "
                eval_str = eval_str + str(Aub[i, j]) + "*x_list[" + str(j) + "]"
                expr_count = expr_count + 1
        eval_str = eval_str + "<=" + str(
            bub[i].reshape(-1, ).tolist()[0][0]) + ", \"vinc_" + get_terminal_part_name_num(i) + "\""

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
                eval_str = eval_str + "==" + str(beq[i].reshape(-1, ).tolist()[0][0]) + ", \"vinceq_" + get_terminal_part_name_num(
                    i + 1 + Aub.shape[0]) + "\""

                prob += eval(eval_str)

    filename = tempfile.NamedTemporaryFile(suffix='.lp').name
    prob.writeLP(filename)
    prob.solve()

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
