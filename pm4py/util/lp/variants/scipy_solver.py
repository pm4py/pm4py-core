import numpy as np
from scipy.optimize import linprog, OptimizeResult
from typing import Optional, Dict, Any, List
from enum import Enum
from pm4py.util import exec_utils


class Parameters:
    INTEGRALITY = "integrality"
    METHOD = "method"


def apply(c: list, Aub: np.ndarray, bub: np.matrix, Aeq: np.matrix, beq: np.matrix,
          parameters: Optional[Dict[Any, Any]] = None) -> OptimizeResult:
    if parameters is None:
        parameters = {}

    integrality = exec_utils.get_param_value(Parameters.INTEGRALITY, parameters, None)
    method = exec_utils.get_param_value(Parameters.METHOD, parameters, "highs" if integrality is None else "highs")
    sol = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, method=method, integrality=integrality)
    return sol


def get_prim_obj_from_sol(sol: OptimizeResult, parameters: Optional[Dict[Any, Any]] = None) -> int:
    if sol.fun is not None:
        return round(sol.fun)


def get_points_from_sol(sol: OptimizeResult, parameters: Optional[Dict[Any, Any]] = None) -> List[int]:
    if sol.x is not None:
        return [round(y) for y in sol.x]
