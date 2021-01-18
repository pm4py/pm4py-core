import sys

from cvxopt import matrix, solvers


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

    solver = parameters["solver"] if "solver" in parameters else None

    c = matrix(c)
    Aub = matrix(Aub)
    bub = matrix(bub)
    if Aeq is not None:
        Aeq = matrix(Aeq)
    if beq is not None:
        beq = matrix(beq)

    solvers.options['glpk'] = {}
    solvers.options['glpk']['LPX_K_MSGLEV'] = 0
    solvers.options['glpk']['msg_lev'] = 'GLP_MSG_OFF'
    solvers.options['glpk']['show_progress'] = False
    solvers.options['glpk']['presolve'] = "GLP_ON"
    solvers.options['glpk']['meth'] = "GLP_PRIMAL"
    solvers.options['msg_lev'] = 'GLP_MSG_OFF'
    solvers.options['show_progress'] = False

    if solver:
        sol = solvers.lp(c, Aub, bub, A=Aeq, b=beq, solver=solver)
    else:
        sol = solvers.lp(c, Aub, bub, A=Aeq, b=beq)

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
    if parameters is None:
        parameters = {}

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
