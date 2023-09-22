import importlib.util

if importlib.util.find_spec("pulp"):
    from pm4py.util.lp.variants import pulp_solver

if importlib.util.find_spec("scipy"):
    from pm4py.util.lp.variants import scipy_solver
