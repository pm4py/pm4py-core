from pm4py.util.lp.versions import pulp_solver
from pm4py.util.lp.versions import ortools_solver

# not available in the latest version of PM4Py
CVXOPT = "cvxopt"
PULP = "pulp"
# not available in the latest version of PM4Py
CVXOPT_SOLVER_CUSTOM_ALIGN = "cvxopt_solver_custom_align"
ORTOOLS_SOLVER = "ortools_solver"

VERSIONS_APPLY = {PULP: pulp_solver.apply, ORTOOLS_SOLVER: ortools_solver.apply}
VERSIONS_GET_PRIM_OBJ = {PULP: pulp_solver.get_prim_obj_from_sol, ORTOOLS_SOLVER: ortools_solver.get_prim_obj_from_sol}
VERSIONS_GET_POINTS_FROM_SOL = {PULP: pulp_solver.get_points_from_sol, ORTOOLS_SOLVER: ortools_solver.get_points_from_sol}


def apply(c, Aub, bub, Aeq, beq, parameters=None, variant=ORTOOLS_SOLVER):
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
    variant
        Variant of the algorithm, possible values: pulp, ortools

    Returns
    -------------
    sol
        Solution of the LP problem by the given algorithm
    """
    return VERSIONS_APPLY[variant](c, Aub, bub, Aeq, beq, parameters=parameters)


def get_prim_obj_from_sol(sol, parameters=None, variant=ORTOOLS_SOLVER):
    """
    Gets the primal objective from the solution of the LP problem

    Parameters
    -------------
    sol
        Solution of the ILP problem by the given algorithm
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm, possible values: pulp, ortools

    Returns
    -------------
    prim_obj
        Primal objective
    """
    return VERSIONS_GET_PRIM_OBJ[variant](sol, parameters=parameters)


def get_points_from_sol(sol, parameters=None, variant=ORTOOLS_SOLVER):
    """
    Gets the points from the solution

    Parameters
    -------------
    sol
        Solution of the LP problem by the given algorithm
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm, possible values: pulp, ortools

    Returns
    -------------
    points
        Point of the solution
    """
    return VERSIONS_GET_POINTS_FROM_SOL[variant](sol, parameters=parameters)
