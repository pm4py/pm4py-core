from cvxopt import matrix, solvers


def apply(c, G, h, A, b, parameters=None):
    """
    Gets the overall solution of the problem

    Parameters
    ------------
    c
        c of an ILP problem
    G
        G of an ILP problem
    h
        h of an ILP problem
    A
        A of an ILP problem
    b
        b of an ILP problem
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    sol
        Solution of the ILP problem by the given algorithm
    """
    if parameters is None:
        parameters = {}

    c = matrix(c, tc='d')
    G = matrix(G)
    h = matrix(h)
    A = matrix(A, tc='d').trans()
    b = matrix(b, tc='d')

    sol = solvers.lp(c, G, h, A, b, solver='glpk', options={'glpk': {'msg_lev': 'GLP_MSG_OFF'}})

    return sol


def get_prim_obj_from_sol(sol, parameters=None):
    """
    Gets the primal objective from the solution of the ILP problem

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
        Solution of the ILP problem by the given algorithm
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    points
        Point of the solution
    """
    if parameters is None:
        parameters = {}

    return [xi for xi in sol['x']]
