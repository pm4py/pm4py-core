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

from cvxopt import blas
from cvxopt import glpk

this_options = {}
this_options["LPX_K_MSGLEV"] = 0
this_options["msg_lev"] = "GLP_MSG_OFF"
this_options["show_progress"] = False
this_options["presolve"] = "GLP_ON"

this_options_lp = {}
this_options_lp["LPX_K_MSGLEV"] = 0
this_options_lp["msg_lev"] = "GLP_MSG_OFF"
this_options_lp["show_progress"] = False
this_options_lp["presolve"] = "GLP_ON"

TOL = 10**(-5)


def check_lp_sol_is_integer(x):
    for i in range(len(x)):
        if abs(x[i] - round(x[i])) > TOL:
            return False
    return True


def custom_solve_ilp(c, G, h, A, b):
    status, x, y, z = glpk.lp(c, G, h, A, b, options=this_options_lp)
    if status == "optimal":
        if not check_lp_sol_is_integer(x):
            size = G.size[1]
            I = {i for i in range(size)}
            status, x = glpk.ilp(c, G, h, A, b, I=I, options=this_options)
        if status == 'optimal':
            pcost = blas.dot(c, x)
        else:
            pcost = None

        return {'status': status, 'x': x, 'primal objective': pcost}
    else:
        return {'status': status, 'x': None, 'primal objective': None}


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
    sol = custom_solve_ilp(c, Aub, bub, Aeq, beq)

    return sol


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
    return sol["primal objective"]


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

    if sol and 'x' in sol and sol['x'] is not None:
        return list(sol['x'])
    else:
        if return_when_none:
            if maximize:
                return [sys.float_info.max] * len(list(var_corr.keys()))
            return [sys.float_info.min] * len(list(var_corr.keys()))
