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
MAX_ALLOWED_HEURISTICS = 10 ** 15

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

if importlib.util.find_spec("cvxopt"):
    from pm4py.util.lp.variants import cvxopt_solver, cvxopt_solver_custom_align, cvxopt_solver_custom_align_ilp, \
        cvxopt_solver_custom_align_arm

    custom_solver = cvxopt_solver_custom_align
    try:
        # for ARM-based Linux, we need to use a different call to GLPK
        if "arm" in str(os.uname()[-1]):
            custom_solver = cvxopt_solver
    except:
        pass

    CVXOPT = "cvxopt"
    CVXOPT_SOLVER_CUSTOM_ALIGN = "cvxopt_solver_custom_align"
    CVXOPT_SOLVER_CUSTOM_ALIGN_ILP = "cvxopt_solver_custom_align_ilp"

    VERSIONS_APPLY[CVXOPT] = cvxopt_solver.apply
    VERSIONS_GET_PRIM_OBJ[CVXOPT] = cvxopt_solver.get_prim_obj_from_sol
    VERSIONS_GET_POINTS_FROM_SOL[CVXOPT] = cvxopt_solver.get_points_from_sol

    VERSIONS_APPLY[CVXOPT_SOLVER_CUSTOM_ALIGN] = custom_solver.apply
    VERSIONS_GET_PRIM_OBJ[CVXOPT_SOLVER_CUSTOM_ALIGN] = custom_solver.get_prim_obj_from_sol
    VERSIONS_GET_POINTS_FROM_SOL[CVXOPT_SOLVER_CUSTOM_ALIGN] = custom_solver.get_points_from_sol

    VERSIONS_APPLY[CVXOPT_SOLVER_CUSTOM_ALIGN_ILP] = cvxopt_solver_custom_align_ilp.apply
    VERSIONS_GET_PRIM_OBJ[
        CVXOPT_SOLVER_CUSTOM_ALIGN_ILP] = cvxopt_solver_custom_align_ilp.get_prim_obj_from_sol
    VERSIONS_GET_POINTS_FROM_SOL[
        CVXOPT_SOLVER_CUSTOM_ALIGN_ILP] = cvxopt_solver_custom_align_ilp.get_points_from_sol

    DEFAULT_LP_SOLVER_VARIANT = CVXOPT_SOLVER_CUSTOM_ALIGN

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
