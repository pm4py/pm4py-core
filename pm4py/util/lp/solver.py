import importlib.util
from enum import Enum


class Parameters(Enum):
    REQUIRE_ILP = "require_ilp"


# not available in the latest version of PM4Py
CVXOPT = "cvxopt"
PULP = "pulp"
SCIPY = "scipy"

# not available in the latest version of PM4Py
CVXOPT_SOLVER_CUSTOM_ALIGN = "cvxopt_solver_custom_align"
CVXOPT_SOLVER_CUSTOM_ALIGN_ILP = "cvxopt_solver_custom_align_ilp"

# max allowed heuristics value (27/10/2019, due to the numerical instability of some of our solvers)
MAX_ALLOWED_HEURISTICS = 10**15

VERSIONS_APPLY = {}
VERSIONS_GET_PRIM_OBJ = {}
VERSIONS_GET_POINTS_FROM_SOL = {}
DEFAULT_LP_SOLVER_VARIANT = None

if importlib.util.find_spec("pulp"):
    # assuming pulp is installed
    from pm4py.util.lp.variants import pulp_solver

    VERSIONS_APPLY[PULP] = pulp_solver.apply
    VERSIONS_GET_PRIM_OBJ[PULP] = pulp_solver.get_prim_obj_from_sol
    VERSIONS_GET_POINTS_FROM_SOL[PULP] = pulp_solver.get_points_from_sol

    DEFAULT_LP_SOLVER_VARIANT = PULP

if importlib.util.find_spec("scipy"):
    # in the case scipy is installed, it works
    from pm4py.util.lp.variants import scipy_solver

    VERSIONS_APPLY[SCIPY] = scipy_solver.apply
    VERSIONS_GET_PRIM_OBJ[SCIPY] = scipy_solver.get_prim_obj_from_sol
    VERSIONS_GET_POINTS_FROM_SOL[SCIPY] = scipy_solver.get_points_from_sol

    DEFAULT_LP_SOLVER_VARIANT = SCIPY


def apply(c, Aub, bub, Aeq, beq, parameters=None, variant=DEFAULT_LP_SOLVER_VARIANT):
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
        Variant of the algorithm, possible values: pulp, scipy

    Returns
    -------------
    sol
        Solution of the LP problem by the given algorithm
    """
    return VERSIONS_APPLY[variant](c, Aub, bub, Aeq, beq, parameters=parameters)


def get_prim_obj_from_sol(sol, parameters=None, variant=DEFAULT_LP_SOLVER_VARIANT):
    """
    Gets the primal objective from the solution of the LP problem

    Parameters
    -------------
    sol
        Solution of the ILP problem by the given algorithm
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm, possible values: pulp, scipy

    Returns
    -------------
    prim_obj
        Primal objective
    """
    return VERSIONS_GET_PRIM_OBJ[variant](sol, parameters=parameters)


def get_points_from_sol(sol, parameters=None, variant=DEFAULT_LP_SOLVER_VARIANT):
    """
    Gets the points from the solution

    Parameters
    -------------
    sol
        Solution of the LP problem by the given algorithm
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm, possible values: pulp, scipy

    Returns
    -------------
    points
        Point of the solution
    """
    return VERSIONS_GET_POINTS_FROM_SOL[variant](sol, parameters=parameters)
