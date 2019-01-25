from pm4py.util.ilp.versions import cvxopt

CVXOPT = "cvxopt"

VERSIONS_APPLY = {CVXOPT: cvxopt.apply}
VERSIONS_GET_PRIM_OBJ = {CVXOPT: cvxopt.get_prim_obj_from_sol}
VERSIONS_GET_POINTS_FROM_SOL = {CVXOPT: cvxopt.get_points_from_sol}


def apply(c, G, h, A, b, parameters=None, variant=CVXOPT):
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
    variant
        Variant of the algorithm, possible values: cvxopt

    Returns
    -------------
    sol
        Solution of the ILP problem by the given algorithm
    """
    return VERSIONS_APPLY[variant](c, G, h, A, b, parameters=parameters)


def get_prim_obj_from_sol(sol, parameters=None, variant=CVXOPT):
    """
    Gets the primal objective from the solution of the ILP problem

    Parameters
    -------------
    sol
        Solution of the ILP problem by the given algorithm
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm, possible values: cvxopt

    Returns
    -------------
    prim_obj
        Primal objective
    """
    return VERSIONS_GET_PRIM_OBJ[variant](sol, parameters=parameters)


def get_points_from_sol(sol, parameters=None, variant=CVXOPT):
    """
    Gets the points from the solution

    Parameters
    -------------
    sol
        Solution of the ILP problem by the given algorithm
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm, possible values: cvxopt

    Returns
    -------------
    points
        Point of the solution
    """
    return VERSIONS_GET_POINTS_FROM_SOL[variant](sol, parameters=parameters)
